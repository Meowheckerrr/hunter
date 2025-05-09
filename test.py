   # 2. assetFinder(Passive) and Alive Check !
    assetFinder_thread = run_tool_as_thread(
    "python3 /root/assetFinder.py",
    "httpx-toolkit -l assets.txt -ports 443,80,8080,8000,888 -threads 200 | anew aliveAssets.txt"
    )

    # 3. subfinder(Passive) and Alive Check 
    subfinder_thread = run_tool_as_thread(
    "subfinder -dL domain.txt | anew subdomains.txt",
    "httpx-toolkit -l subdomains.txt -ports 443,80,8080,8000,888 -threads 200 | anew aliveSubDomains.txt"
    )

    assetFinder_thread.join()
    subfinder_thread.join()