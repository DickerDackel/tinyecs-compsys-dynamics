tinyecs-compsys-dynamics API
============================

.. contents::
   :class: this-will-duplicate-information-and-it-is-still-useful-here

Components
----------

Registers the following CIDs to ``tinyecs.compsys.Comp``:

* AIM_AT
* ALIGN_MOMENTUM
* ALIGN_WITH
* ANCHOR
* FRICTION
* LERP_ALPHA
* LERP_ANGLE
* LERP_MOMENTUM
* LERP_POSITION
* LERP_SCALE
* MOMENTUM
* PRSA
* TRACK_DIRECT
* TRACK_PROPNAV

.. autoclass:: tinyecs.compsys.dynamics.Anchor
   :members:

.. autoclass:: tinyecs.compsys.dynamics.LerpPosition
   :members:

.. autoclass:: tinyecs.compsys.dynamics.PRSA
   :members:

.. autoclass:: tinyecs.compsys.dynamics.TrackDirect
   :members:

.. autoclass:: tinyecs.compsys.dynamics.TrackPropNav
   :members:


Systems
-------

.. autofunction:: tinyecs.compsys.dynamics._angle_of
.. autofunction:: tinyecs.compsys.dynamics.sys_aim_at
.. autofunction:: tinyecs.compsys.dynamics.sys_align_momentum
.. autofunction:: tinyecs.compsys.dynamics.sys_align_with
.. autofunction:: tinyecs.compsys.dynamics.sys_anchor
.. autofunction:: tinyecs.compsys.dynamics.sys_friction
.. autofunction:: tinyecs.compsys.dynamics.sys_gravity
.. autofunction:: tinyecs.compsys.dynamics.sys_lerp_alpha
.. autofunction:: tinyecs.compsys.dynamics.sys_lerp_angle
.. autofunction:: tinyecs.compsys.dynamics.sys_lerp_momentum
.. autofunction:: tinyecs.compsys.dynamics.sys_lerp_position
.. autofunction:: tinyecs.compsys.dynamics.sys_lerp_scale
.. autofunction:: tinyecs.compsys.dynamics.sys_momentum
.. autofunction:: tinyecs.compsys.dynamics.sys_track_direct
.. autofunction:: tinyecs.compsys.dynamics.sys_track_propnav
