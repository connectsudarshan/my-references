# Shared tooling for the NVMe and ZNS study pages

Rebuild a page (from this folder's parent):

    python3 study_common/build.py NVMe_QA_src      # writes NVMe_QA_src/out/NVMe_QA_Study_Guide.html
    python3 study_common/build.py ZNS_QA_src
    python3 study_common/build.py NVMe_QA_src --check NVMe_QA_src/content/m05.txt   # validate one file

Redraw diagrams: run the diag_*.py files in a topic folder, then `python3 study_common/merge_diagrams.py <topic_dir>`.
Render figures to PNG for a visual check: `python3 study_common/figpreview.py <topic_dir> diagrams_A.js`.
Regression test a built page (needs Playwright + Chromium):
    python3 study_common/test_page.py NVMe_QA_src/out/NVMe_QA_Study_Guide.html nvmeqa.v1 1.02 1.03 3.09
Content format is documented at the top of build.py and in each topic's AUTHORING.md.
