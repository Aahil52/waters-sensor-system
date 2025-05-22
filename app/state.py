from threading import Lock

# Internal shared state (dictionary of latest sensor values)
_state = {
    "sensor_ready": False,
    "last_update": None,
    "uptime": None,
    "turbidity": None,
    "temperature": None,
    "total_dissolved_solids": None,
    "pH": None
}
_state_lock = Lock()

def update_state(new_data: dict):
    # Thread-safe update of the shared state.
    with _state_lock:
        _state.update(new_data)

def get_state() -> dict:
    # Returns a copy of the current state to avoid accidental mutation.
    with _state_lock:
        return _state.copy()