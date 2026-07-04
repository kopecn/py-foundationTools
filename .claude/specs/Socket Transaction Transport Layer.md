# Spec: Socket Transaction Transport Layer

## 1. SocketHandler (Base Transport Primitive)

### Responsibilities

- Owns raw `socket.socket`
- Manages recv thread lifecycle
- Dispatches:
    - raw byte chunks → data handler
    - UTF-8 tokens → string handler

### Guarantees

- thread-safe socket swap (`_attach_socket`, `_detach_socket`)
- recv loop is single-threaded per socket instance
- safe teardown via:
    - explicit `disconnect()`
    - `atexit` cleanup

---

### Receive Model

Each recv iteration:
