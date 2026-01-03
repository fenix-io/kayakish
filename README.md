# Kayak Calculation Tool (kayakish)

This tool is intended to provide a simple solution to the complex kayak or small boat calculations.
The tool is intended to work as an API server and host a HTML UI allowing the input of the hull data, and finding centers of gravity/buoyancy, doing analysis of displacement and building stability curves with different loads, so you can have an early idea about the behavior expected from the hull.


---

## Design
Application is built using
- Python 3.11+ as the main language
- Pydantic and FastAPI for the API interface
- Numpy for the raw calculations
- Application will be eventually contained in a docker for simple usage and deployment 



