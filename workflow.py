"""Lesson-specific workflow. Read this file before the execution adapter."""
from __future__ import annotations
import asyncio
import json
from pathlib import Path
from runtime import atomic_json, contained_path, in_process_tool

async def run(agent, data):
    plan = await agent.ask('planner', 'Create a plan using only collect and summarize actions; dependencies must refer to earlier step IDs.', data,
        {'steps': [{'id': 's1', 'action': 'collect', 'depends_on': []}, {'id': 's2', 'action': 'summarize', 'depends_on': ['s1']}]})
    completed = {}
    for step in plan['steps']:
        if step['id'] in completed or step['action'] not in {'collect', 'summarize'} or not set(step['depends_on']) <= completed.keys():
            raise ValueError('Invalid action, duplicate ID or unsatisfied dependency')
        if step['action'] == 'collect':
            completed[step['id']] = data['facts']
        else:
            completed[step['id']] = await agent.ask('executor_' + step['id'], 'Summarize the collected facts.', completed,
                'Discover paths with Glob, read content with Read, and inspect ResultMessage for the outcome.')
    return {'plan': plan, 'completed': completed}
