import React from 'react';
import * as d3 from 'd3';

function TreeDiagram({ data }) {
  React.useEffect(() => {
    if (data) {
      // Clear any existing SVG
      d3.select('#tree-container').selectAll('*').remove();

      // Setup dimensions and margins
      const width = 600;
      const height = 400;

      const svg = d3.select('#tree-container')
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .append('g')
        .attr('transform', 'translate(50, 50)');

      const hierarchyData = d3.hierarchy(dataStructure(data))
        .sum(d => d.children ? 0 : 1);

      const treeLayout = d3.tree().size([width - 100, height - 100]);
      treeLayout(hierarchyData);

      svg.selectAll('line')
        .data(hierarchyData.links())
        .enter()
        .append('line')
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y)
        .attr('stroke', 'black');

      svg.selectAll('circle')
        .data(hierarchyData.descendants())
        .enter()
        .append('circle')
        .attr('cx', d => d.x)
        .attr('cy', d => d.y)
        .attr('r', 5)
        .attr('fill', 'blue');

      svg.selectAll('text')
        .data(hierarchyData.descendants())
        .enter()
        .append('text')
        .attr('x', d => d.x + 10)
        .attr('y', d => d.y)
        .text(d => d.data.name);
    }
  }, [data]);

  return <div id="tree-container"></div>;
}

// Helper function to transform MongoDB data to a hierarchy
function dataStructure(data) {
  const children = data.sampled_by.map(sample => ({
    name: sample.track_name,
    children: sample.artists.map(artist => ({ name: artist }))
  }));

  return {
    name: data.original_song,
    children: children
  };
}

export default TreeDiagram;
