# hunter

## Structure
project/
├── main.py                # Main entry point
├── results/
│   └── interesting/       # Critical scanning results
│       ├── aliveAssets.txt
│       ├── aliveSubDomains.txt
│       ├── waffSubDomains.json
│       └── no_waf_domains.txt
├── logs/
│   ├── app.log            # Main application log
│   └── normal/            # Intermediate files and logs
│       ├── subdomains.txt
│       ├── assets.txt
│       ├── burp.log
│       ├── assetFinder.log
│       ├── subfinder.log
│       ├── wafw00f.log
│       └── thread.log
└── utils/
    ├── logging_config.py  # Centralized logging configuration
    ├── config.py          # Constants and configurations
    ├── subprocess_utils.py # Subprocess utilities
    ├── file_utils.py      # File-related utilities
    └── network_utils.py   # Network-related utilities


---------------------------------------------------------------------


