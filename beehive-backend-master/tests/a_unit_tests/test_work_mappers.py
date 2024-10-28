from src.logic.work_mappers.base import deflate_mapper, inflate_mapper
from src.logic.work_mappers.code_modification import CodeModificationMapper
from src.logic.work_mappers.code_review import CodeReviewMapper
from src.models.work import WorkType


def test_code_review_mapper_deflate_inflate():
    mapper = CodeReviewMapper()

    # deflate and re-inflate the mapper
    deflated_mapper = deflate_mapper(mapper)
    inflated_mapper = inflate_mapper(deflated_mapper)

    # code review mapper holds no properties
    assert type(inflated_mapper) == type(mapper)


def test_code_modification_work_mapper_deflate_inflate():
    mapper = CodeModificationMapper(WorkType.CREATE_FUNCTION, 3)

    # deflate and re-inflate the mapper
    deflated_mapper = deflate_mapper(mapper)
    inflated_mapper = inflate_mapper(deflated_mapper)

    # make sure all property values survived the process
    assert type(inflated_mapper) == type(mapper)
    assert inflated_mapper.original_work_type == mapper.original_work_type
    assert inflated_mapper.remaining_modifications_count == mapper.remaining_modifications_count
