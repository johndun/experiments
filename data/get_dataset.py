from datasets import load_dataset, load_from_disk
import os

def get_dataset(dataset_name_or_path):
    """
    Load a dataset from a local path or from the Hugging Face Hub.

    Args:
        dataset_name_or_path (str): The name of the dataset to load or the local path to the dataset.

    Returns:
        Dataset: The loaded dataset.
    """
    if os.path.exists(dataset_name_or_path):
        # Load dataset from local path
        dataset = load_from_disk(dataset_name_or_path)
    else:
        # Load dataset from Hugging Face Hub
        dataset = load_dataset(dataset_name_or_path)
    
    return dataset
