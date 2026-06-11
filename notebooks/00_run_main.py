# Databricks notebook source
# MAGIC %md
# MAGIC # GA4 Report — Main Job Wrapper
# MAGIC
# MAGIC Instala dependências e executa o relatório principal.

# COMMAND ----------

# MAGIC %pip install -r ../requirements.txt

# COMMAND ----------

import os
import sys

repo_root = os.path.dirname(os.path.dirname(os.path.abspath("__file__")))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

os.environ.setdefault("GA4_ENV", "databricks")

# COMMAND ----------

dbutils.widgets.text("analysis_start", "")
dbutils.widgets.text("analysis_end", "")
dbutils.widgets.text("output_dir", "")

# COMMAND ----------

for key, widget in [
    ("GA4_ANALYSIS_START", "analysis_start"),
    ("GA4_ANALYSIS_END", "analysis_end"),
    ("GA4_OUTPUT_DIR", "output_dir"),
]:
    value = dbutils.widgets.get(widget)
    if value:
        os.environ[key] = value

# COMMAND ----------

from jobs.run_main import main

main()
