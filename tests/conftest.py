import os
import vcr

test_dir = os.path.dirname(__file__)
test_data_dir = os.path.join(test_dir, "cassettes")

vcr.default_vcr = vcr.VCR(
    cassette_library_dir=test_data_dir,
    path_transformer=vcr.VCR.ensure_suffix('.yaml'),
    record_mode='once',
)
vcr.use_cassette = vcr.default_vcr.use_cassette
