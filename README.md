# Maven scanner

Identify Maven projects from local mirrors and build each project. Collect sonar stats and jqassistant scan after builing each project.

## jqassistnt

To check if there Spring related results are collected (during analyze phase), run the following command
the current version (2.0.0) of spring plugin does not work well with neo4j 5.x. No errors are shown but no Spring objects are identified during the analysis run. Use neo4j 4.x instead.

```shell
cypher-shell -a localhost -u neo4j -p password \
 "MATCH (n:Spring) RETURN labels(n) as NodeLabels, COUNT(*) as Count ORDER BY NodeLabels;"
```
