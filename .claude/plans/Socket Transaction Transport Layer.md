# Concept Plan: Socket Transaction Transport Layer

## Overview

The socket subsystem provides a **bidirectional, pluggable transport layer** that supports:

- raw byte transport (TCP sockets)
- string tokenization (delimiter-based streaming)
- binary framing (codec-based)
- transactional routing (tx_id correlation)

It is designed to be:

- transport-agnostic at upper layers
- codec-pluggable at protocol layer
- concurrency-safe and thread-driven at runtime

---

## Core Design Philosophy

### 1. Composition over inheritance

All socket behavior is composed:

- `SocketHandler` owns socket + recv thread
- Clients/servers extend behavior via layering, not subclassing sockets

### 2. Dual-channel receive model

Every socket emits **two independent streams**:

- Raw bytes stream → `data_handler`
- Token stream → `string_handler`

These operate simultaneously and do not interfere.

---

### 3. Layered protocol stacking

The architecture is explicitly layered:
