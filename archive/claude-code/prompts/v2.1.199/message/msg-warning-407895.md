---
id: msg-warning-407895
name: Warning Message
category: message
subcategory: warning
source_line: 407895
---

,
        ),
        h
      );
    }),
    r = Fs(),
    o = Hx.useRef(null),
    [s, i] = Hx.useState(null),
    a = Hx.useRef(null),
    l = Hx.useRef(new Map()),
    c = Hx.useRef(new Set()),
    u = Hx.useRef(new Set()),
    [d] = Hx.useState(fNn),
    p = Hx.useCallback((h) => {
      c.current.add(h);
    }, []),
    f = Hx.useCallback((h) => {
      c.current.delete(h);
    }, []),
    m = Hx.useCallback(() => {
      (a.current?.(), (a.current = null));
    }, []),
    g = Hx.useCallback(
      (h) => {
        if ((m(), h !== null))
          a.current = r.setTimeout(() => {
            (T("[keybindings] Chord timeout - cancelling"),
              (o.current = null),
              i(null));
          }, ZYa);
        ((o.current = h), i(h));
      },
      [m, r],
    );
  return (
    Hx.useEffect(() => {
      bQi(P4);
      let h = P4.changed.subscribe((y) => {
        (n(y),
          T(
            
