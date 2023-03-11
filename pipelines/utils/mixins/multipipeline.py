class MultiPipelineMixin:
    def get_pipeline(self):
        return self.pipeline[self.action]
