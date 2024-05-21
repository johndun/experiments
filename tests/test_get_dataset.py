import os
import pytest
from data.get_dataset import get_dataset

def test_load_local_dataset():
    dataset_path = 'test_data/tiny_mnist'
    dataset = get_dataset(dataset_path)
    assert dataset is not None
    assert 'train' in dataset
    assert 'test' in dataset

def test_load_hub_dataset():
    dataset_name = 'mnist'
    dataset = get_dataset(dataset_name)
    assert dataset is not None
    assert 'train' in dataset
    assert 'test' in dataset

if __name__ == "__main__":
    pytest.main()
