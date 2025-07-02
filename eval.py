from intelligence_layer.core import Task, TaskSpan
from pharia_skill.testing import DevCsi
import time
import json
from blusql.skill.generate_query import Input, Output, generate_query


class Text2SQLEvaluationTask(Task):
    def __init__(self):
        self.dev_csi = DevCsi().with_studio(project="qa-marius")
        ## Load dataset once
        # with open("data/test-data/examples.json") as f:
        #    self.test_data = json.load(f)

    def do_run(self, input: Input, task_span: TaskSpan) -> Output:
        start_time = time.time()
        output = generate_query(self.dev_csi, input)
        duration = time.time() - start_time

        return Output(answer=output.answer, duration=duration)


# if main == __main__:
