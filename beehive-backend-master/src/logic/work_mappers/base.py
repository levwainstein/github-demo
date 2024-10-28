from abc import ABC, abstractmethod
import json


class BaseWorkMapper(ABC):
    @abstractmethod
    def map_work(self, completed_work, completed_work_record):
        raise NotImplementedError

    @abstractmethod
    def get_init_params(self):
        raise NotImplementedError


DEFLATED_MAPPER_SEPARATOR = '|-|'


def all_mapper_classes():
    from .code_review import CodeReviewMapper
    from .code_modification import CodeModificationMapper
    from .check_reusability import CheckReusabilityMapper
    from .code_qa import CodeQAMapper

    return [CodeReviewMapper, CodeModificationMapper, CheckReusabilityMapper, CodeQAMapper]


def deflate_mapper(mapper):
    deflated_parts = [mapper.__class__.__name__]
    deflated_parts.append(json.dumps(mapper.get_init_params()))
    return DEFLATED_MAPPER_SEPARATOR.join(deflated_parts)


def inflate_mapper(deflated_mapper):
    deflated_parts = deflated_mapper.split(DEFLATED_MAPPER_SEPARATOR)

    for MapperClass in all_mapper_classes():
        if MapperClass.__name__ == deflated_parts[0]:
            return MapperClass(*json.loads(deflated_parts[1]))

    raise Exception(f'failed to inflate mapper of class "{deflated_parts[0]}" with params {deflated_parts[1]}')
