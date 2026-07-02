---
id: msg-warning-360781
name: Warning Message
category: message
subcategory: warning
source_line: 360781
---

,
        ),
        h
      );
    }),
    r = Is(),
    o = dI.useRef(null),
    [s, i] = dI.useState(null),
    a = dI.useRef(null),
    l = dI.useRef(new Map()),
    c = dI.useRef(new Set()),
    u = dI.useRef(new Set()),
    [d] = dI.useState(Kkn),
    p = dI.useCallback((h) => {
      c.current.add(h);
    }, []),
    f = dI.useCallback((h) => {
      c.current.delete(h);
    }, []),
    m = dI.useCallback(() => {
      (a.current?.(), (a.current = null));
    }, []),
    g = dI.useCallback(
      (h) => {
        if ((m(), h !== null))
          a.current = r.setTimeout(() => {
            (T("[keybindings] Chord timeout - cancelling"),
              (o.current = null),
              i(null));
          }, fka);
        ((o.current = h), i(h));
      },
      [m, r],
    );
  return (
    dI.useEffect(() => {
      qBi(J2);
      let h = J2.changed.subscribe((y) => {
        (n(y),
          T(
            
