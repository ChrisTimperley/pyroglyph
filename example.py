# -*- coding: utf-8 -*-
import pyroglyph


block_resources = pyroglyph.Block('Resources', [
    'Running Time: 00d 01h 31m 46s',
    'Num. Candidates: 5470',
    'Num. Test Executions: 29786'
])
window = pyroglyph.Window('Darjeeling', [block_resources], [])
window.run()
