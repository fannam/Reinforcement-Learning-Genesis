# Basic Humanoid

Humanoid MJCF/XML tối giản để test render và simulation trong Genesis.

File chính:

```text
robots/basic_humanoid/basic_humanoid.xml
```

Robot gồm:

- `pelvis` với `freejoint` để robot có thể rơi/chuyển động tự do.
- `torso`, `head`.
- Hai tay: shoulder, elbow.
- Hai chân: hip, knee, ankle, foot.
- Actuator motor cho các joint 1D.
