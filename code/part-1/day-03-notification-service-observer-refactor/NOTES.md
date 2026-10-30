- Cycle 1: the Zero test forced channels to be passed into the constructor, so tests can hand in fakes.
- Cycle 2: sending needed something to send, so the test introduced a Notification value object (frozen dataclass).
- Cycle 3: the SMS test exposed the hardcoded email channel, so send now looks the channel up by name.
- Cycle 4: asserting on the return value forced send to return a SendResult instead of None, so callers can see what happened.
- Cycle 5: the unknown-name test replaced a leaking KeyError with a domain error, UnknownChannelError.
- Cycle 6: the Many test added send_many, which reuses send, so results come back in the order the names were given.
- Cycle 7: the failing-channel test made ChannelError part of the channel contract; send turns it into SendResult(ok=False) instead of crashing.
- Cycle 7: send_many kept going after a failure with no new code, because it reuses send; the second test only locks that in.
- Cycle 8: the boundary test made send_many check every channel name before sending anything, so a typo can't cause a half-sent batch.
- Cycle 9: real channels keep their own in-memory sent list, the same shape as FakeChannel, so nothing is really sent.
- Cycle 9: each channel checks its own input and raises ChannelError, so email rules live in EmailChannel, not in the service.
- Cycle 10: a second channel with the same validate-then-record shape led to a _RecordingChannel base class; each channel only adds its own recipient rule.
- Cycle 12: the contract the tests had relied on since cycle 1 was written down as a Channel Protocol; the service is typed against Channel, never a concrete channel.

## Observer refactor

- Cycle O1: the first observer test made the service the subject — it keeps a list of observers (empty at start) and tells each one the same SendResult it returns.
- Cycle O5: unsubscribe is list.remove, so an observer is found by equality (identity for plain classes) and the service still needs no knowledge of what observers do.
