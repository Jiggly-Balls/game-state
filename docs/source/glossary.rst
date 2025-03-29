Glossary
========

This glossary provides definitions for key terms used in the ``game-state``
library. It serves as a reference for understanding the core components and
functionalities that help manage game states, transitions, and listener handling.

.. glossary::

    Global Listener
        A Global Listener functions similarly to a :term:`State Listener` but is triggered
        universally, if defined. It responds to the same predefined conditions as 
        regular listeners but executes before the corresponding State Listener.
        Global Listeners do not override State Listeners; instead, they run 
        alongside them, allowing for additional global behavior.

    State
        A State represents a distinct screen, scene, or phase within a game. It defines
        a specific part of the game's flow, such as a main menu, gameplay level, or
        pause screen. States help manage transitions and ensure that different parts of
        the game function independently while maintaining overall game logic.
    
    State Hook
        A State Hook links states that are defined across multiple files, enabling
        fluid integration and communication between them. It typically works by
        iterating through specified file paths to connect and manage these states,
        ensuring they function cohesively within the game's state management system.

    State Listener
        A State Listener is a method within the State class that responds to specific
        conditions or transitions. Examples include ``on_setup``, ``on_enter``, and
        ``on_leave``, which execute automatically at key moments in a state's
        lifecycle. Listeners help manage state changes by running predefined logic when
        certain events occur.

    State Manager
        The State Manager handles the organization and transition of different :term:`State`
        within a game. It allows for seamless switching between states, ensuring that
        each state is properly initialized, updated, and cleaned up. This helps
        maintain a structured game flow and simplifies state management for developers.

    Update Model
        The ``game-state`` library uses a hybrid update model, combining both push-based
        and pull-based approaches. Event-driven Listeners trigger immediate updates
        when specific conditions occur (push-based), ensuring responsiveness. At the
        same time, the system periodically pulls state updates as part of the game loop
        (pull-based), ensuring consistency. This balance optimizes performance while
        maintaining flexibility in state management.

.. :toctree::

   guide