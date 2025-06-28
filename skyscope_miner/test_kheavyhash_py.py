import unittest
import os
import sys

# Ensure the miner directory is in the Python path for imports
# This is a common way to handle imports when running tests from a different directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# project_root = os.path.dirname(current_dir) # If tests were in a subfolder like 'tests/'
# sys.path.insert(0, project_root)
sys.path.insert(0, current_dir) # If test file is in the same dir as modules

try:
    from kheavyhash_py import (
        keccak_256,
        bytes_to_int_list,
        int_list_to_bytes,
        initialize_matrix,
        multiply_matrices_conceptual,
        hash_matrix_state_conceptual,
        kheavyhash_conceptual_python,
        KHEAVYHASH_MATRIX_SIZE # Use the configured matrix size for tests
    )
except ImportError:
    print("Error: Could not import from kheavyhash_py. Ensure it's in the Python path.")
    print(f"Current sys.path: {sys.path}")
    # Fallback for tool execution if relative import fails, assuming flat structure for tool
    from skyscope_miner.kheavyhash_py import (
        keccak_256,
        bytes_to_int_list,
        int_list_to_bytes,
        initialize_matrix,
        multiply_matrices_conceptual,
        hash_matrix_state_conceptual,
        kheavyhash_conceptual_python,
        KHEAVYHASH_MATRIX_SIZE
    )


class TestKHeavyHashConceptual(unittest.TestCase):

    def test_keccak_256_output_length(self):
        """Test that keccak_256 returns 32 bytes."""
        data = b"test data"
        hashed = keccak_256(data)
        self.assertEqual(len(hashed), 32)

    def test_keccak_256_deterministic(self):
        """Test that keccak_256 is deterministic."""
        data = b"another test string"
        hash1 = keccak_256(data)
        hash2 = keccak_256(data)
        self.assertEqual(hash1, hash2)

    def test_keccak_256_different_inputs_produce_different_outputs(self):
        """Test that different inputs produce different keccak_256 outputs."""
        data1 = b"input1"
        data2 = b"input2"
        self.assertNotEqual(keccak_256(data1), keccak_256(data2))

    def test_bytes_int_list_conversion(self):
        """Test bytes_to_int_list and int_list_to_bytes."""
        original_bytes = b'\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00' # Two 64-bit little-endian ints: 1 and 2
        num_elements = 2
        element_size = 8

        int_list = bytes_to_int_list(original_bytes, num_elements, element_size)
        self.assertEqual(int_list, [1, 2])

        converted_bytes = int_list_to_bytes(int_list, element_size)
        self.assertEqual(original_bytes, converted_bytes)

        # Test with padding
        short_bytes = b'\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00' # 12 bytes
        int_list_padded = bytes_to_int_list(short_bytes, num_elements, element_size)
        # Expects [1, 512] because 0x0200000000000000 becomes [1, 0x02000000] effectively if only 4 bytes of 2nd element exist
        # The current bytes_to_int_list pads with \x00 at the end of the *chunk* if data is short.
        # So the second element becomes int.from_bytes(b'\x02\x00\x00\x00\x00\x00\x00\x00', 'little') if padded correctly
        # The current padding logic might be tricky if total data < num_elements * element_size
        # For this specific input, the second chunk is b'\x02\x00\x00\x00' + b'\x00\x00\x00\x00' = 2
        self.assertEqual(int_list_padded, [1, 2])


    def test_initialize_matrix_dimensions(self):
        """Test if initialize_matrix returns a matrix of correct dimensions."""
        seed = b"matrix_seed"
        size = KHEAVYHASH_MATRIX_SIZE # Use configured size
        matrix = initialize_matrix(seed, size)
        self.assertEqual(len(matrix), size)
        if size > 0:
            self.assertEqual(len(matrix[0]), size)

    def test_multiply_matrices_conceptual_dimensions(self):
        """Test if matrix multiplication returns a matrix of correct dimensions."""
        size = KHEAVYHASH_MATRIX_SIZE
        # Create dummy matrices
        matrix_a = [[(r*size + c + 1) for c in range(size)] for r in range(size)]
        matrix_b = [[(r*size + c + 2) for c in range(size)] for r in range(size)]

        if size == 0: # Skip if matrix size is 0
            return

        result = multiply_matrices_conceptual(matrix_a, matrix_b, size)
        self.assertEqual(len(result), size)
        self.assertEqual(len(result[0]), size)

    def test_hash_matrix_state_conceptual_output_length(self):
        """Test output length of conceptual matrix state hashing."""
        size = KHEAVYHASH_MATRIX_SIZE
        matrix = [[(r*size + c) for c in range(size)] for r in range(size)]
        hashed_state = hash_matrix_state_conceptual(matrix, size)
        self.assertEqual(len(hashed_state), 32) # Keccak-256 output

    def test_kheavyhash_conceptual_python_runs_and_output_length(self):
        """Test that the main conceptual kHeavyHash function runs and produces 32-byte output."""
        header_data = b"some header data for testing" + os.urandom(32) # Add randomness
        hashed_output = kheavyhash_conceptual_python(header_data)
        self.assertIsNotNone(hashed_output)
        if hashed_output is not None: # Guard for type checker
             self.assertEqual(len(hashed_output), 32)

    def test_kheavyhash_conceptual_deterministic(self):
        """Test that the conceptual kHeavyHash is deterministic."""
        header_data = b"deterministic test input string"
        hash1 = kheavyhash_conceptual_python(header_data)
        hash2 = kheavyhash_conceptual_python(header_data)
        self.assertEqual(hash1, hash2)

    def test_kheavyhash_conceptual_avalanche(self):
        """Test that a small change in input creates a very different output."""
        header_data1 = b"avalanche test string1"
        # Create header_data2 with a single bit flip from header_data1
        temp_list = list(header_data1)
        temp_list[-1] = temp_list[-1] ^ 1 # Flip the last bit of the last byte
        header_data2 = bytes(temp_list)

        self.assertNotEqual(header_data1, header_data2) # Ensure inputs are different

        hash1 = kheavyhash_conceptual_python(header_data1)
        hash2 = kheavyhash_conceptual_python(header_data2)
        self.assertNotEqual(hash1, hash2)

        # A more rigorous avalanche test would count differing bits,
        # expecting roughly 50% for a good hash function.
        # This basic check is sufficient for this conceptual implementation.
        if hash1 and hash2: # Ensure not None
            diff_bits = 0
            for b1, b2 in zip(hash1, hash2):
                diff_bits += bin(b1 ^ b2).count('1')
            # print(f"Avalanche differing bits: {diff_bits} out of {len(hash1)*8}")
            self.assertTrue(diff_bits > (len(hash1) * 8) * 0.25, "Hash outputs too similar for different inputs") # Expect at least 25% bits different

if __name__ == '__main__':
    # This allows running the tests directly from the command line
    # Navigate to the directory containing this file and run: python test_kheavyhash_py.py
    # Or, if it's part of a larger test suite: python -m unittest skyscope_miner.test_kheavyhash_py

    # Ensure the kheavyhash_py module can be found
    # This setup assumes test_kheavyhash_py.py is in the same directory as kheavyhash_py.py
    # or that the skyscope_miner directory is in PYTHONPATH.

    # The following is a bit of a hack for direct execution if modules are not found.
    # It's better to run tests using `python -m unittest discover` from the project root
    # or `python -m unittest skyscope_miner.test_kheavyhash_py`
    if "kheavyhash_py" not in sys.modules and "skyscope_miner.kheavyhash_py" not in sys.modules :
        print("Attempting to adjust sys.path for direct test execution if module not found...")
        # This might be needed if you run `python test_kheavyhash_py.py` from within skyscope_miner/
        # and kheavyhash_py is intended to be imported as `from .kheavyhash_py import ...`
        # However, the current import `from kheavyhash_py import ...` assumes it's directly findable
        # or `skyscope_miner` is already in path.
        # For the tool's sandbox, direct import from the module often works if in same dir.
        pass

    unittest.main()
