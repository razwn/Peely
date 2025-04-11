import json
import os
import argparse
from langchain.document_loaders import WebBaseLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils.pinecone_utils import get_pinecone_index


def load_sources_config(config_path):
    """Load content sources configuration from JSON file"""
    with open(config_path, 'r') as f:
        return json.load(f)


def load_website(source_config):
    """Load content from a website"""
    print(f"Loading website: {source_config['name']}")
    location = source_config['location']

    # Use sitemap or direct URL
    if location.endswith('sitemap.xml'):
        # For sitemap, we'd need a custom implementation or use a 3rd party library
        # For simplicity, we'll just extract the base URL
        base_url = location.replace('/sitemap.xml', '')
        loader = WebBaseLoader(base_url)
    else:
        # Direct URL
        loader = WebBaseLoader(location)

    # Load documents
    documents = loader.load()

    # Apply blacklist filtering if specified
    if 'blacklist' in source_config:
        blacklist = source_config['blacklist']
        filtered_docs = []

        for doc in documents:
            # Check if the document URL contains any blacklisted strings
            if not any(
                blacklist_item in doc.metadata.get('source', '')
                for blacklist_item in blacklist
            ):
                filtered_docs.append(doc)

        documents = filtered_docs

    return documents


def load_directory(source_config):
    """Load content from a directory"""
    print(f"Loading directory: {source_config['name']}")
    location = source_config['location']

    # Use appropriate glob pattern based on need
    glob_pattern = source_config.get('glob_pattern', '**/*.txt')

    print(f"Directory path: {os.path.abspath(location)}")
    print(f"Using glob pattern: {glob_pattern}")

    # Check if directory exists
    if not os.path.exists(location):
        print(f"WARNING: Directory '{location}' does not exist!")
        return []

    # Check directory contents
    print("Directory contents:")
    for item in os.listdir(location):
        item_path = os.path.join(location, item)
        if os.path.isfile(item_path):
            print(f"  - File: {item} ({os.path.getsize(item_path)} bytes)")
        else:
            print(f"  - Dir: {item}/")

    # Initialize directory loader
    loader = DirectoryLoader(
        path=location,
        glob=glob_pattern,
        recursive=True
    )

    # Load documents
    try:
        documents = loader.load()
        print(f"Successfully loaded {len(documents)} documents")
    except Exception as e:
        print(f"Error loading documents: {str(e)}")
        documents = []

    return documents


def chunk_documents(documents, chunk_size):
    """Split documents into chunks"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=int(chunk_size * 0.1),  # 10% overlap
        length_function=len
    )

    return text_splitter.split_documents(documents)


def main():
    parser = argparse.ArgumentParser(
        description='Load knowledge base content into Pinecone')
    parser.add_argument('--config', type=str, required=True,
                        help='Path to content sources configuration JSON file')
    args = parser.parse_args()

    # Load configuration
    config = load_sources_config(args.config)

    # Get Pinecone index
    pinecone_index = get_pinecone_index()

    # Process each content source
    all_chunks = []
    for source in config['content_sources']:
        source_type = source['type']
        chunk_size = source.get('chunk_size', 512)

        # Load documents based on source type
        if source_type == 'Website':
            documents = load_website(source)
        elif source_type == 'Directory':
            documents = load_directory(source)
        else:
            print(f"Unsupported source type: {source_type}")
            continue

        # Chunk documents
        chunks = chunk_documents(documents, chunk_size)
        all_chunks.extend(chunks)

        print(
            f"Loaded {len(documents)} documents, created {len(chunks)} chunks from {source['name']}"
        )

    # Upload chunks to Pinecone
    print(f"Uploading {len(all_chunks)} chunks to Pinecone...")

    if len(all_chunks) == 0:
        print("No documents to upload.")
        return

    # Get the vector store with the embedding model already configured
    pinecone_index = get_pinecone_index()

    # Batch upload in groups of 100
    batch_size = 100
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i + batch_size]

        # Using the from_documents method which handles the embedding process internally
        if i == 0:  # Only for the first batch, use from_documents to create the index
            try:
                # We've already configured the embedding model when we got the vector store
                texts = [doc.page_content for doc in batch]
                metadatas = [doc.metadata for doc in batch]

                # Add the texts directly
                pinecone_index.add_texts(texts=texts, metadatas=metadatas)
                print(
                    (
                        f"Uploaded batch {i // batch_size + 1}/"
                        f"{(len(all_chunks) + batch_size - 1) // batch_size}"
                    )
                )
            except Exception as e:
                print(f"Error uploading batch: {str(e)}")
                raise
        else:
            # For subsequent batches
            texts = [doc.page_content for doc in batch]
            metadatas = [doc.metadata for doc in batch]

            # Add the texts directly
            pinecone_index.add_texts(texts=texts, metadatas=metadatas)
            print(
                f"Uploaded batch {i // batch_size + 1}/"
                f"{(len(all_chunks) + batch_size - 1) // batch_size}"
            )

    print("Knowledge base loading complete!")


if __name__ == "__main__":
    main()
