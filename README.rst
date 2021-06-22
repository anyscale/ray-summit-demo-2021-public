Ray Support Bot demo
--------------------

Note that we are not able to provide the trained models, so actual ML models are mocked out (we just return random messages for the chatbot).

Setup
-----

Install dependencies with ``pip install --use-deprecated=legacy-resolver -U -r requirements.txt``.

Training
--------

Run ``python train.py``

To run many tune trials: ``python train.py --num-trials <num_trials>``


Run Chatbot
-----------

Start Ray and run the Ray Serve deploy script:

.. code-block:: bash

  ray start --head
  python chatbot.py

Navigate to ``localhost:8000`` to see the UI.

Frontend
--------

The frontend code is hosted by the FastAPI app in Ray Serve. The code is in ``frontend/``.

Utils
-----

The Grafana dashboard JSON and file for Locust load testing are in ``util/``.

CI
--

CI is not configured to run on this repository, but the code is in ``.github/workflows/deploy.yml.``
