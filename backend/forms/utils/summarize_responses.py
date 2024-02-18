"""
Builds a summary of responses to a survey.
See ../tests.py:test_summarize_responses for examples.
"""

from collections import Counter
from enum import Enum
from typing import Any, Literal

import pydantic

from ..models.field import Field, FieldType

# NOTE: Keep in sync with frontend/src/components/SchemaForm/models.ts


class SummaryType(str, Enum):
    TEXT = "Text"
    SINGLE_CHECKBOX = "SingleCheckbox"
    SELECT = "Select"
    MATRIX = "Matrix"
    FILE_UPLOAD = "FileUpload"


class BaseFieldSummary(pydantic.BaseModel):
    # XXX(pyright): pyright does not understand populate_by_name=True, hence javaScriptCase here
    countResponses: int
    countMissingResponses: int


class TextFieldSummary(BaseFieldSummary):
    type: Literal[SummaryType.TEXT] = SummaryType.TEXT
    summary: list[str]


class FileUploadSummary(BaseFieldSummary):
    type: Literal[SummaryType.FILE_UPLOAD] = SummaryType.FILE_UPLOAD
    summary: list[str]


class SingleCheckboxSummary(BaseFieldSummary):
    """
    For a single checkbox field, there is no separation between "not answered" and "not checked".
    Hence the summary is the number of responses that had the checkbox checked, and that is
    provided in the countResponses field.
    """

    type: Literal[SummaryType.SINGLE_CHECKBOX] = SummaryType.SINGLE_CHECKBOX


class SelectFieldSummary(BaseFieldSummary):
    type: Literal[SummaryType.SELECT] = SummaryType.SELECT
    summary: dict[str, int]


class MatrixFieldSummary(BaseFieldSummary):
    type: Literal[SummaryType.MATRIX] = SummaryType.MATRIX
    summary: dict[str, dict[str, int]]


FieldSummary = TextFieldSummary | SingleCheckboxSummary | SelectFieldSummary | MatrixFieldSummary | FileUploadSummary
Summary = dict[str, FieldSummary]


def summarize_responses(fields: list[Field], valuesies: list[dict[str, Any]]) -> Summary:
    summary: Summary = {}

    total_responses = len(valuesies)

    for field in fields:
        match field.type:
            case FieldType.STATIC_TEXT | FieldType.SPACER | FieldType.DIVIDER:
                pass

            # TODO: handle htmlType="number" for high cardinality fields
            case FieldType.SINGLE_LINE_TEXT if field.html_type == "number":
                field_summary = Counter()

                for value in valuesies:
                    value = value.get(field.slug)
                    if value is None:
                        continue

                    # javascript object keys are always strings
                    value = str(value)

                    field_summary[value] += 1

                count_responses = sum(field_summary.values())
                count_missing_responses = total_responses - count_responses

                summary[field.slug] = SelectFieldSummary(
                    countResponses=count_responses,
                    countMissingResponses=count_missing_responses,
                    summary=dict(field_summary),
                )

            # TODO(#436) Time zone handling
            case (
                FieldType.SINGLE_LINE_TEXT
                | FieldType.MULTI_LINE_TEXT
                | FieldType.DATE_FIELD
                | FieldType.TIME_FIELD
                | FieldType.DATE_TIME_FIELD
            ):
                field_summary = []

                for values in valuesies:
                    value = values.get(field.slug)
                    if value is None:
                        continue

                    value = str(value).strip()
                    if not value:
                        continue

                    field_summary.append(value)

                count_responses = len(field_summary)
                count_missing_responses = total_responses - count_responses

                summary[field.slug] = TextFieldSummary(
                    countResponses=count_responses,
                    countMissingResponses=count_missing_responses,
                    summary=field_summary,
                )

            case FieldType.FILE_UPLOAD:
                field_summary = []
                count_responses = 0

                for values in valuesies:
                    value = values.get(field.slug, [])

                    if not value:
                        continue

                    count_responses += 1

                    field_summary.extend(value)

                count_missing_responses = total_responses - count_responses

                summary[field.slug] = FileUploadSummary(
                    countResponses=count_responses,
                    countMissingResponses=count_missing_responses,
                    summary=field_summary,
                )

            case FieldType.SINGLE_CHECKBOX:
                count_responses = sum(1 for values in valuesies if values.get(field.slug))
                count_missing_responses = total_responses - count_responses

                summary[field.slug] = SingleCheckboxSummary(
                    countResponses=count_responses,
                    countMissingResponses=count_missing_responses,
                )

            case FieldType.SINGLE_SELECT:
                field_summary = {choice.slug: 0 for choice in field.choices or []}

                for values in valuesies:
                    value = values.get(field.slug)
                    if value:
                        if field.type == FieldType.SINGLE_CHECKBOX:
                            value = "true"
                        else:
                            value = str(value)

                        # account for the possibility of a choice being removed
                        field_summary.setdefault(value, 0)
                        field_summary[value] += 1

                count_responses = sum(field_summary.values())
                count_missing_responses = total_responses - count_responses

                summary[field.slug] = SelectFieldSummary(
                    summary=dict(field_summary),
                    countResponses=count_responses,
                    countMissingResponses=count_missing_responses,
                )

            case FieldType.MULTI_SELECT:
                field_summary = {choice.slug: 0 for choice in field.choices or []}
                count_responses = 0

                for values in valuesies:
                    values = values.get(field.slug, [])

                    if not values:
                        continue

                    count_responses += 1

                    for value in values:
                        # account for the possibility of a choice being removed
                        field_summary.setdefault(value, 0)
                        field_summary[value] += 1

                count_missing_responses = total_responses - count_responses

                summary[field.slug] = SelectFieldSummary(
                    countResponses=count_responses,
                    countMissingResponses=count_missing_responses,
                    summary=dict(field_summary),
                )

            case FieldType.RADIO_MATRIX:
                field_summary = {}
                questions = field.questions or []
                choices = field.choices or []

                for question in questions:
                    # note: removed questions will not be included in the summary
                    question_summary = {choice.slug: 0 for choice in choices}

                    for values in valuesies:
                        value = values.get(field.slug, {}).get(question.slug)
                        if value is not None:
                            # account for the possibility of a choice being removed
                            question_summary.setdefault(value, 0)
                            question_summary[value] += 1

                    field_summary[question.slug] = dict(question_summary)

                # these are more meaningful on a per-question basis but provided for completeness
                count_responses = sum(
                    1 for values in valuesies if any(answer for answer in values.get(field.slug, {}).values())
                )
                count_missing_responses = total_responses - count_responses

                summary[field.slug] = MatrixFieldSummary(
                    countResponses=count_responses,
                    countMissingResponses=count_missing_responses,
                    summary=field_summary,
                )

    return summary
