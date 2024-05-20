import argparse
from datasets import load_dataset, DatasetDict

def initialize_test_image_data(dataset_name):
    # Load the dataset
    dataset = load_dataset(dataset_name)
    
    # Create a tiny version of the dataset containing the 1st 8 samples per split
    tiny_dataset = {split: data.select(range(8)) for split, data in dataset.items()}
    
    # Convert the dictionary of splits to a DatasetDict
    tiny_dataset_dict = DatasetDict(tiny_dataset)
    
    # Save the DatasetDict to the specified directory
    save_path = f"test_data/tiny_{dataset_name}"
    tiny_dataset_dict.save_to_disk(save_path)
    print(f"Tiny dataset saved to {save_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize a tiny version of the dataset.")
    parser.add_argument("--dataset_name", type=str, required=True, help="Name of the dataset to initialize.")
    args = parser.parse_args()
    
    initialize_test_image_data(args.dataset_name)
