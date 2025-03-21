title: Hypergraphs

---

Learning and thinking about hypergraphs!

---

I recently came across [hypergraphs](https://en.wikipedia.org/wiki/Hypergraph)
in short, hypergraphs generalize the concept of an edge to be a relationship
across some set of nodes and not just a pair of nodes. There's also directed
hypergraphs, which seem to also add in a notion of direction in the sense of
having a set of nodes that point to some other set of nodes.

I'm not too familiar with any of the domains where hypergraphs seem to naturally
arise, but reading about it gave me some insights on (typed) property graphs. In
some ways, I think directed hypergraphs sounds like a "schema" for a property
graph, and a hypergraph itself sounds like a way to encode types and properties
into the graph structure itself. It's also possible to view building indices
over a property graph as constructing a hypergraph.
