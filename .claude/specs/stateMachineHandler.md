---
spec: StateMachineHandler
scope: project
last_updated: 2026-09-11
semver: 0.0.7
author: Nicholas Bergantz
---

# State Machine Handler

## Scope

This specification defines the durable behavioral contract of the state-machine handler: declarative definitions, transition selection, lifecycle, hierarchy, callbacks, and observation. It also governs optional supporting components for coordination, event-bus communication, and definition visualization.

The specification governs what the handler must do, not the mechanisms used to do it. Exact class members, private fields, storage models, internal event encodings, callback-binding internals, delivery mechanisms, iteration order, and context-copying strategies are not compatibility requirements unless a separate approved contract establishes them.

A top-level handler invocation SHALL process its supplied stimulus within that invocation. Scheduling and concurrency across top-level invocations belong to callers.

This specification does not establish behavior for unresolved callback names, action recovery after callback failure, or mutable-data ownership between parent and child contexts. Those behaviors require explicit decisions before they become requirements.

## Architectural Boundary

A handler executes one state-machine definition and maintains the mutable state associated with that definition.

The handler SHALL separate declarative state-machine definitions from mutable handler state.

Definitions SHALL describe machine structure and behavior using serializable data. Executable guards and actions SHALL be referenced by name rather than embedded as callable objects.

The handler SHALL provide state tracking, callback invocation, delay-transition eligibility, and observation without making those concerns part of the serialized definition.

The handler SHALL support horizontal composition through independent machines and vertical composition through machines nested within states.

## Definition Model

A state-machine definition SHALL represent:

- a machine identifier
- a collection of states
- an initial state
- a collection of directed transitions

A runnable state-machine definition SHALL identify an initial state.

A state definition SHALL represent:

- an identifier
- an optional human-readable label
- optional named entry, exit, and tick actions
- terminal or non-terminal status
- an optional nested state-machine definition
- optional application metadata

A transition definition SHALL represent:

- an identifier
- a source state
- a target state
- an optional triggering event
- an optional named guard
- an optional named action
- an optional delay
- a priority

The definition model SHALL remain independent of handler context, active state, pending stimuli, callback implementations, timing state, and observers.

## Handler Context

Each handler SHALL maintain a context that makes the following information available to behavioral callbacks:

- machine identity
- current state
- previous state
- the stimulus associated with the current transition or entry
- application-defined mutable data

The context SHALL persist for the handler's lifetime.

Before state-entry behavior runs, the handler SHALL update the context to identify the entered state, the previously active state, and the triggering stimulus.

Definitions SHALL NOT contain mutable handler data.

## Initialization

A handler SHALL be initialized before it processes stimuli.

Initialization SHALL enter the definition's initial state using normal state-entry semantics, with no previous state and no triggering stimulus.

Initialization SHALL occur at most once during a handler's lifetime.

Initialization SHALL complete any automatic-transition chain resulting from initial state entry before initialization completes.

A handler SHALL reject initialization of a definition that does not identify a valid initial state.

## Stimulus Processing

A handler SHALL process one top-level stimulus at a time. A stimulus submitted while a top-level stimulus is being processed SHALL be deferred until that top-level processing turn completes, including all resulting transition lifecycle activity and automatic transitions.

Each handler, including a child handler, SHALL apply this processing boundary independently. Deferred stimuli SHALL be processed in submission order.

The handler SHALL support stimuli originating from:

- external events
- explicit ticks
- delay expiration
- nested-machine completion

Stimulus scheduling, timing measurement, and delivery are caller concerns and are not governed by this specification.

## Transition Eligibility

For an external event, eligible transitions SHALL include outgoing transitions whose declared event matches the stimulus.

An automatic transition is specifically an outgoing transition with neither a triggering event nor a delay. Delayed transitions are not automatic transitions under this definition.

Automatic transitions SHALL be considered:

- after entering a non-terminal state
- after processing a tick action
- when processing an external event

Automatic transitions SHALL NOT require a matching external event, but they SHALL be evaluated only when handler activity triggers evaluation.

When a declared transition's delay expires, the caller MAY submit a delay-expiration stimulus identifying that transition. The handler SHALL consider the transition only if its declared source state is currently active.

A delay-expiration stimulus for a transition whose declared source state is not currently active SHALL have no effect.

A transition that declares both an event and a delay MAY become eligible through either the matching event or expiration of its delay.

Nested-machine completion SHALL be exposed to the parent as a stimulus that can make parent transitions eligible. The encoding of that stimulus is not governed here.

## Deterministic Selection

When multiple transitions are eligible, the handler SHALL evaluate them in descending priority order. Equal-priority candidates SHALL use a deterministic tie-breaker whose mechanism is not governed here.

The handler SHALL select the first eligible transition whose guard passes and SHALL stop evaluating lower-ranked candidates for that stimulus.

A transition without a guard SHALL pass guard evaluation.

A named guard SHALL be resolved by the handler and evaluated against the current context. Guard results SHALL use Boolean interpretation.

A false guard result is normal non-selection and SHALL NOT produce an error observation.

If guard execution raises an exception, the transition SHALL NOT be selected, the failure SHALL be observable through the handler's error-observation mechanism, and evaluation SHALL continue with the next candidate.

## Tick Semantics

A tick SHALL evaluate behavior for the currently active non-terminal state.

The caller SHALL determine tick cadence and submit each tick to the handler.

When the active state declares a tick action, that action SHALL run before automatic-transition guards are evaluated.

At most one transition SHALL be selected from a tick evaluation.

## State Entry

Normal state entry SHALL occur in this order:

1. update the handler context
2. notify state-change observers when entry follows a previous state
3. run the state's entry action, when defined
4. apply terminal-state behavior when the entered state is terminal
5. otherwise activate its nested machine, if defined
6. evaluate automatic transitions

Because automatic transitions are evaluated on entry, successful automatic transitions MAY form an immediate chain across multiple states.

## Transition Lifecycle

The normal lifecycle for a selected transition SHALL occur in this order:

1. exit the source state
2. run the transition action, when defined
3. notify transition observers
4. enter the target state

Source-state exit SHALL deactivate its nested machine and make delay-expiration stimuli for its outgoing transitions ineffective before running the source state's exit action.

The normal behavioral-action order SHALL therefore be source exit action, transition action, then target entry action.

## Terminal States

Entering a terminal state SHALL run its entry behavior before completing the machine.

Terminal completion SHALL:

- make delay-expiration stimuli ineffective
- mark the handler terminal
- stop subsequent stimulus processing
- notify terminal observers with the terminal state's identity

A terminal state SHALL NOT activate a nested machine, make delayed transitions eligible, or evaluate automatic transitions.

Consumers SHALL be able to obtain the terminal state's identity when the machine completes.

Terminal completion SHALL end the handler lifecycle permanently. Subsequent stimuli SHALL have no effect, and a new handler SHALL be created to execute the definition again.

## Hierarchical Machines

Entering a state with a nested definition SHALL associate and initialize a child handler for that definition.

The child SHALL follow the same transition and lifecycle semantics as an independent handler.

Leaving a composite state SHALL deactivate its associated non-terminal child hierarchy from the innermost child outward. Each non-terminal associated child's current-state exit action SHALL run before its enclosing child's exit action and before the parent state's exit action.

When the child reaches a terminal state, the parent SHALL receive a completion stimulus that permits parent transition selection.

A non-composite state SHALL have no associated child handler. A composite state SHALL have at most one associated child handler corresponding to its nested definition while the parent remains in that state.

A child that reaches a terminal state SHALL process no further stimuli but MAY remain associated with its composite parent state until the parent leaves that state. Parent exit SHALL disassociate a terminal child without invoking additional child lifecycle callbacks.

## Callback Model

The handler SHALL resolve named guards and actions through a callback registry or equivalent binding mechanism.

Behavioral callback roles SHALL remain distinct:

- guards determine transition eligibility
- transition actions represent behavior associated with taking an edge
- entry actions represent behavior associated with entering a state
- exit actions represent behavior associated with leaving a state
- tick actions represent periodic behavior while a state is active

Callback invocation SHALL follow the handler lifecycle ordering. Scheduling beyond the handler call is caller-owned.

Guards, actions, and observers SHALL execute synchronously within the handler invocation. Asynchronous work MAY be initiated by application callbacks, but such work is outside the handler's lifecycle semantics.

Guard execution failure SHALL follow the rejection and observation behavior defined under Deterministic Selection. Failures from actions SHALL be observable, but their recovery and lifecycle effects are not governed by this specification.

Callback failure SHALL NOT leave the handler with an invalid current state, an associated child belonging to a different state, or delayed-transition eligibility belonging to an inactive state.

This structural integrity guarantee does not require rollback of application data or callback side effects.

## Observation

The handler SHALL support multiple observers for:

- state changes
- selected transitions
- terminal completion
- callback errors

State-change observation SHALL identify the previous and entered states.

Transition observation SHALL identify the selected transition and expose its associated handler context.

Terminal observation SHALL identify the terminal state.

Error observation SHALL expose the callback failure and associated context.

An observer failure SHALL be contained without invoking error observers. It SHALL NOT alter handler state, interrupt the lifecycle being observed, or prevent remaining observers for that observation from being invoked.

## Coordination

A coordinator SHALL manage multiple independent handlers without becoming a state machine itself.

Each coordinated handler SHALL retain independent state, context, stimuli, delayed-transition eligibility, hierarchy, and terminal status.

Coordination SHALL support:

- adding, removing, and resolving named handlers
- targeted event delivery
- broadcast event delivery
- ticking managed handlers
- determining terminal completion of managed handlers with each completion associated with its registered handler name

Completion of one managed handler SHALL be determinable independently of the terminal status of other managed handlers.

The exact coordinator method names, delivery order, and iteration strategy are not governed by this specification.

## Event Bus

The optional event bus SHALL provide publish/subscribe communication independently of handler transition processing and coordinator ownership.

An event-bus publication SHALL associate an event name with an optional application payload and deliver it to subscribers.

Failure of one event-bus subscriber SHALL NOT prevent delivery to other subscribers.

Subscription storage, dispatch ordering, snapshot behavior, and delivery mechanisms are implementation concerns.

## Visualization

The visualization layer SHALL produce its representation solely from declarative state-machine definition data.

Visualization SHALL be ancillary: handler behavior SHALL NOT depend on visualization availability or output.

The visualization contract does not govern output styling or rendering implementation.

## Compliance

A compliant state-machine handler MUST demonstrate these observable outcomes:

1. A definition can be represented without executable callback references or mutable handler state.
2. Initialization occurs at most once, enters a valid initial state through normal state-entry semantics, completes resulting automatic transitions, and rejects definitions without a valid initial state.
3. Each handler processes one top-level stimulus at a time and processes deferred submissions in submission order only after the current processing turn and resulting automatic transitions complete.
4. Competing eligible transitions resolve deterministically by descending priority, deterministic tie-breaking, and first passing guard.
5. Automatic, tick-driven, event-driven, delayed, and child-completion stimuli follow their specified eligibility rules.
6. Normal state entry, state exit, and transition behavior follow the specified lifecycle ordering.
7. A transition-specific delay-expiration stimulus has no effect after its source state ceases to be active.
8. Terminal completion permanently ends the handler lifecycle, prevents subsequent processing, and exposes the terminal state's identity.
9. A non-composite state has no associated child; a composite state has at most one associated child corresponding to its nested definition; non-terminal child teardown runs from the innermost child outward; and a terminal child remains inactive while associated, exposes completion to the parent, and is disassociated without additional lifecycle callbacks.
10. Guards, actions, and observers execute synchronously within the handler invocation while application-initiated asynchronous work remains outside handler lifecycle semantics.
11. False guard results are normal non-selection; guard exceptions reject that candidate, remain observable, and permit evaluation of the next candidate; action failures remain observable without prescribing recovery or lifecycle effects, while callback failures preserve the stated structural invariants without requiring rollback of application side effects.
12. Observer failures are contained without invoking error observers and do not alter state, interrupt the observed lifecycle, or prevent remaining observer notifications.
13. Coordinated handlers retain independent state and associate terminal completion with registered handler names.
14. One event-bus subscriber's failure does not prevent delivery to other subscribers.
15. When visualization is absent, state-machine handling remains unchanged.
