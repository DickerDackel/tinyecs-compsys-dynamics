from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from math import copysign

import glm
import tinyecs as ecs

from aenum import extend_enum
from glm import vec2
from pgcooldown import LerpThing
from tinyecs import EntityID
from tinyecs.compsys import Comp

extend_enum(Comp, 'AIM_AT')
extend_enum(Comp, 'ALIGN_MOMENTUM')
extend_enum(Comp, 'ALIGN_WITH')
extend_enum(Comp, 'ANCHOR')
extend_enum(Comp, 'FRICTION')
extend_enum(Comp, 'LERP_ALPHA')
extend_enum(Comp, 'LERP_ANGLE')
extend_enum(Comp, 'LERP_MOMENTUM')
extend_enum(Comp, 'LERP_POSITION')
extend_enum(Comp, 'LERP_SCALE')
extend_enum(Comp, 'MOMENTUM')
extend_enum(Comp, 'PRSA')
extend_enum(Comp, 'TRACK_HOMING')
extend_enum(Comp, 'TRACK_DIRECT')


@dataclass
class Anchor:
    """A component to position one entity relative to another.

    :param parent: The entity ID of the entity to hook on
    :param offset: The offset relative to the parent

    """

    parent: EntityID
    offset: vec2


@dataclass
class LerpPosition:
    """A component for a timed move between two points.

    :param start: The start position
    :param direction: A normalized direction vector
    :param progress: A LerpThing to track the distance over time

    """

    start: vec2
    direction: vec2
    progress: LerpThing


class PRSA:
    """Rotation, Scale, Alpha, Position in one container"""
    pos: vec2
    rotation: float
    scale: float
    alpha: float

    def __init__(self, pos: vec2, rotation: float = 0, scale: Sequence | float = 1, alpha: float = 255) -> None:
        self.pos = vec2(pos) if pos is not None else vec2()
        self.rotation = rotation
        self.scale = scale
        self.alpha = alpha

    def __iter__(self) -> Iterator[object]:
        yield self.pos
        yield self.rotation
        yield self.scale
        yield self.alpha

    def __repr__(self) -> str:
        return f'PRSA(pos={self.pos}, rotation={self.rotation}, scale={self.scale}, alpha={self.alpha})'


@dataclass
class TrackDirect:
    """Configuration data for direct tracking

    :param target: EntityID of the target to track
    :param splash_radius: Distance at which the target is considered caught

    """

    target: EntityID
    splash_radius: float = 0


@dataclass
class TrackPropNav:
    """Configuration data for proportional navigation tracking

    :param target: EntityID of the target to track
    :param allowed_angle: The angle the entity can turn between steps
    :param splash_radius: Distance at which the target is considered caught

    """

    target: EntityID
    allowed_angle: float = 180
    splash_radius: float = 0
    _prev_los: float | None = field(init=False, default_factory=lambda: None)
    # ^ Internal, line of sight during the previous call.


def _angle_of(v: vec2) -> float:
    """Return the angle of ``v`` in degrees, since glm lacks that.

    :param v: The vector in question
    :return: Angle of ``v`` in degrees

    """

    return glm.degrees(glm.atan2(v.y, v.x))


def sys_aim_at(eid: EntityID, prsa: PRSA, aim_at: EntityID) -> None:
    """Update prsa.rotation to point towards the target.

    :param eid: The entity ID
    :param prsa: The PRSA transform object of the entity

    """

    pprsa = ecs.comp_of_eid(aim_at, Comp.PRSA)
    delta = pprsa.pos - prsa.pos
    prsa.rotation = _angle_of(delta)


def sys_align_momentum(eid: EntityID, prsa: PRSA, momentum: vec2, align_momentum: bool):
    """Align the entity with its own momentum.

    :param eid: The entity ID

    """

    if not momentum: return

    prsa.rotation = _angle_of(momentum)


def sys_align_with(eid: EntityID, prsa: PRSA, align_with: EntityID) -> None:
    """Align rotation with rotation of parent.

    :param eid: The entity ID

    """

    pprsa = ecs.comp_of_eid(align_with, Comp.PRSA)
    prsa.rotation = pprsa.rotation


def sys_anchor(eid: EntityID, prsa: PRSA, anchor: Anchor) -> None:
    """Position the entity relative to its parent.

    :param eid: The entity ID

    """

    pprsa = ecs.comp_of_eid(anchor.parent, Comp.PRSA)
    rad = glm.radians(pprsa.rotation)
    real_offset = glm.rotate(anchor.offset, rad) * pprsa.scale
    prsa.pos = pprsa.pos + real_offset


def sys_friction(eid: EntityID, momentum: vec2, friction: float, *, dt: float) -> None:
    """Apply friction to the momentum.

    :param eid: The entity ID
    :param eid: The momentum of the entity
    :param friction: The friction to apply
    :param dt: Deltatime

    FIXME implementation undecided
    """

    if not friction: return
    if not momentum: return

    reduce = (1 - friction * dt)
    momentum *= reduce


def sys_gravity(eid: EntityID, momentum: vec2, gravity: vec2, *, dt: float) -> None:
    """Apply gavity to both momentum and position.

    :param eid: The entity ID
    :param prsa: The PRSA transform object of the entity
    :param momentum: The momentum of the entity
    :param gravity: The world gravity to apply
    :param dt: Delta time

    """

    momentum += gravity * dt


def sys_lerp_alpha(eid: EntityID, lerp: LerpThing, prsa: PRSA) -> None:
    """Lerp the alpha of the entity.

    :param eid: The entity ID
    :param lerp: A `pgcooldown.LerpThing` for the alpha change.

    """

    prsa.alpha = lerp()
    if lerp.finished():
        ecs.remove_component(Comp.LERP_ALPHA)


def sys_lerp_angle(eid: EntityID, lerp: LerpThing, prsa: PRSA) -> None:
    """Lerp the orientation of the entity.

    :param eid: The entity ID
    :param lerp: A `pgcooldown.LerpThing` for the rotation change.

    """

    prsa.rotation = lerp()
    if lerp.finished():
        ecs.remove_component(Comp.LERP_ANGLE)


def sys_lerp_momentum(eid: EntityID, lerp: LerpThing, momentum: vec2) -> None:
    """Lerp the scale of the entity.

    :param eid: The entity ID
    :param lerp: A `pgcooldown.LerpThing` for the momentum change.

    """

    momentum.xy = glm.normalize(momentum) * lerp()
    if lerp.finished():
        ecs.remove_component(Comp.LERP_MOMENTUM)


def sys_lerp_position(eid: EntityID, prsa: PRSA, lerp: LerpPosition):
    """Update position based on a LerpPosition object.

    :param eid: The entity ID
    :param prsa: The PRSA transform object of the entity
    :param lerp: The ``LerpPosition`` object tracking the distance

    .. note:: Moving an object with this method conflicts doing it by momentum.
    """

    progress = lerp.progress
    prsa.pos = lerp.start + lerp.direction * progress
    if lerp.progress.finished():
        ecs.remove_component(eid, Comp.LERP_POSITION)


def sys_lerp_scale(eid: EntityID, lerp: LerpThing, prsa: PRSA) -> None:
    """Lerp the scale of the entity.

    :param eid: The entity ID
    :param lerp: A `pgcooldown.LerpThing` for the scale change.

    """

    prsa.scale = lerp()
    if lerp.finished():
        ecs.remove_component(Comp.LERP_SCALE)


def sys_momentum(eid: EntityID, prsa: PRSA, momentum: vec2, *, dt: float) -> None:
    """Apply momentum to the PRSA.

    :param eid: The entity ID
    :param prsa: The PRSA transform object of the entity
    :param momentum: The momentum of the entity
    :param dt: Delta time

    """

    prsa.pos += momentum * dt


def sys_track_direct(eid: EntityID, prsa: PRSA, momentum: vec2, target: TrackDirect) -> None:
    """Track another target, make the momentum point directly towards it.

    :param eid: The entity ID
    :param prsa: The PRSA transform object of the entity
    :param momentum: The momentum of the entity
    :param target: The entity ID of the target

    """

    pprsa = ecs.comp_of_eid(target, Comp.PRSA)
    delta = pprsa.pos - prsa.pos

    if glm.length(delta) < 32:
        ecs.add_component(eid, Comp.IS_KILLED, True)
        return

    rad = glm.atan2(delta.y, delta.x)
    direction = glm.rotate(vec2(1, 0), rad)
    direction *= glm.length(momentum)
    momentum.xy = direction.xy


def sys_track_prop_nav(eid: EntityID, prop_nav: TrackPropNav, prsa: PRSA, momentum: vec2, *, dt: float):
    """Make the entity track another entity by proportional navigation.

    :param eid: The entity ID
    :param prop_nav: The configuration object for the targetting
    :param prsa: The PRSA transform object of the entity
    :param momentum: The momentum of the entity
    :param dt: Delta time

    """

    position = prsa.pos
    pprsa = ecs.comp_of_eid(prop_nav.target, Comp.PRSA)
    target = pprsa.pos

    def normalize(phi):
        return (phi % 360) - 180

    los = target - position
    angle = _angle_of(los)
    los_phi = normalize(angle)

    if glm.length(los) < 8:
        ecs.add_component(eid, Comp.IS_KILLED, True)
        return

    if prop_nav._prev_los is None:
        prop_nav._prev_los = los_phi
        return

    delta_phi = normalize(prop_nav._prev_los - los_phi)
    if delta_phi == 0:
        return

    prop_nav._prev_los = los_phi

    rotation = min(prop_nav.allowed_angle * dt, abs(delta_phi))
    rad = glm.radians(rotation)
    new_momentum = glm.rotate(momentum, copysign(rad, delta_phi))
    momentum.xy = new_momentum.xy
