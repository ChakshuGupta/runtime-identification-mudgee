import unittest

from src.compute import compute_static_similarity, compute_dynamic_similarity


class TestCompute(unittest.TestCase):
    def test_compute_dynamic_similarity(self):
        """
        Test dynamic similarity score computation
        """
        num_matches = 10
        runtime_profile_set_size = 100

        score = compute_dynamic_similarity(num_matches, runtime_profile_set_size)

        self.assertEqual(score, 0.1)

    def test_compute_static_similarity(self):
        """
        Test static similarity score computation
        """
        num_matches = 10
        mud_profile_set_size = 100

        score = compute_static_similarity(num_matches, mud_profile_set_size)

        self.assertEqual(score, 0.1)

    def test_find_intersection(self):
        """
        TODO: Add test for this!
        """
        pass


if __name__ == '__main__':
    unittest.main()