import os

class WLT_ENVIRONMENT_MANAGER(object):
    """A global object that reads environment variables and generates paths for them"""

    def ev_test_print(self):
        # profile = os.environ.get('SOMEPATH')
        # to_path = os.path.abspath(profile)
        print(os.environ.get('SOMEPATH'))