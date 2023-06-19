from pipelines.base import BasePipeItem


class AddMentionOnComment(BasePipeItem):
    def _run(self):
        pipeline = self.pipeline

        mention = pipeline.user
        comment = pipeline.comment

        comment.mentions.add(mention)
        comment.save()
