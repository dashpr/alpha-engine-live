name: Daily Alpha Engine Run

on:
  schedule:
    # Runs every day at 14:30 UTC = 8:00 PM India time
    - cron: "30 14 * * *"

  workflow_dispatch:  # allows manual run from GitHub button

jobs:
  run-alpha:
    runs-on: ubuntu-latest

    steps:
      # 1️⃣ Checkout repo
      - name: Checkout repository
        uses: actions/checkout@v4

      # 2️⃣ Setup Python
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      # 3️⃣ Install dependencies
      - name: Install dependencies
        run: |
          pip install pandas numpy yfinance

      # 4️⃣ Run the cloud alpha engine
      - name: Run Cloud Alpha Engine
        run: |
          python CLOUD_ALPHA_RUNNER.py

      # 5️⃣ Commit outputs ONLY if they exist (safe production logic)
      - name: Commit updated outputs
        run: |
          git config --global user.name "alpha-bot"
          git config --global user.email "alpha-bot@users.noreply.github.com"

          if [ -d "output" ] && [ "$(ls -A output 2>/dev/null)" ]; then
            git add output/*
            git commit -m "Daily alpha engine update" || echo "No changes to commit"
            git push
          else
            echo "No output files to commit"
          fi
