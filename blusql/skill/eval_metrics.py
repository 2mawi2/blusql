from pharia_skill.testing import DevCsi
from generate_query import Input, Output
import difflib
from pharia_skill import ChatParams, Message
from pydantic import BaseModel
from collections.abc import Iterable
from typing import Iterable
from statistics import mean
from intelligence_layer.evaluation import (
    Example,
    AggregationLogic,
    SingleOutputEvaluationLogic,
)


import logging
import math

from pharia_skill import TopLogprobs, ChatResponse
from pharia_skill.testing import DevCsi
from jinja2 import Template
from abc import ABC


class ExpectedOutput(BaseModel):
    sql_query: str


class Checker(ABC):

    def __init__(self) -> None:
        self.dev_csi = DevCsi().with_studio("test-studio")
        self.evaluation_model = "llama-3.3-70b-instruct"
        self.logger = logging.getLogger(__name__)

    def get_metric(
        self, question: str, expected_answer: str, generated_answer: str
    ) -> ChatResponse:
        system_prompt = self.system_prompt
        user_prompt = self.user_prompt.format(
            question=question,
            expected_answer=expected_answer,
            generated_answer=generated_answer,
        )

        messages = [
            Message.system(system_prompt),
            Message.user(user_prompt),
            Message.assistant("Score: "),
        ]
        params = ChatParams(max_tokens=10, temperature=0.0, logprobs=TopLogprobs(10))
        response = self.dev_csi.chat(
            model=self.evaluation_model, messages=messages, params=params
        )

        content = response.message.content.strip()
        fallback_score = self.parse_score(content)

        probs = getattr(response, "logprobs", None)
        if (
            not probs
            or not hasattr(probs, "__getitem__")
            or len(probs) < 2
            or not hasattr(probs[-2], "top")
        ):
            self.logger.warning("No logprobs found")
            return fallback_score

        logprobs = probs[-2].top
        return self.compute_weighted_score(logprobs, fallback_score)

    @staticmethod
    def parse_score(score_str: str) -> float:
        """Convert score string to float if valid, else return fallback"""
        return (
            float(score_str)
            if score_str.isdigit() and 0 <= float(score_str) <= 10
            else 1
        )

    @staticmethod
    def compute_weighted_score(logprobs, fallback_score: float) -> float:
        """Compute weighted score from token logprobs"""
        digit_probs = {
            float(prob.token): math.exp(prob.logprob)
            for prob in logprobs
            if prob.token.isdigit() and 0 <= float(prob.token) <= 10
        }

        total = sum(digit_probs.values())
        if total == 0:
            return fallback_score

        normalized = {k: v / total for k, v in digit_probs.items()}
        return round(sum(k * v for k, v in normalized.items()), 1)


class AccuracyChecker(Checker):

    def __init__(self) -> None:
        super().__init__()
        self.system_prompt = """
        You are a highly precise evaluation assistant specialized in assessing factual accuracy and correctness.

        Your task is to evaluate how accurately the generated answer reflects the facts and information from the expected answer.

        SCORING RUBRIC (1-10):
        - 9-10: Highly accurate - No factual errors, all claims correctly supported
        - 7-8: Mostly accurate - Minor factual discrepancies or unclear statements
        - 5-6: Moderately accurate - Some factual errors but generally correct direction
        - 3-4: Low accuracy - Multiple factual errors or significant misrepresentations
        - 1-2: Poor accuracy - Major factual errors, contradicts expected information

        EVALUATION CRITERIA:
        1. Are specific facts, figures, and data points correct?
        2. Are the claims and statements supported by the expected information?
        3. Are there any contradictions with the expected answer?
        4. Is the information presented without distortion or misinterpretation?

        Return only a single integer score between 1 and 10. 
        """
        self.user_prompt: Template = """
        TASK: Evaluate the factual accuracy of the generated answer against the expected reference answer.

        QUESTION:
        {question}

        EXPECTED ANSWER (Reference):
        {expected_answer}

        GENERATED ANSWER (To Evaluate):
        {generated_answer}

        EVALUATION STEPS:
        1. Identify factual claims, data points, and specific information in both answers
        2. Compare the accuracy of facts, figures, dates, and other verifiable information
        3. Check for any contradictions or misrepresentations
        4. Assess whether claims are properly supported by the reference information

        IMPORTANT: Respond with ONLY a single integer from 1 to 10. Do not include any explanation or additional text.
        """


class FactualityChecker(Checker):
    def __init__(self) -> None:
        super().__init__()
        self.system_prompt = """
        You are a highly precise evaluation assistant specialized in assessing information precision and relevance.

        Your task is to evaluate how well the generated answer stays grounded in relevant information without adding hallucinated or irrelevant content.

        SCORING RUBRIC (1-10):
        - 9-10: Excellent precision - Only relevant information, no hallucinations or fabrications
        - 7-8: Good precision - Mostly relevant content, minimal irrelevant information
        - 5-6: Fair precision - Some irrelevant details or minor unsupported claims
        - 3-4: Poor precision - Significant irrelevant content or unverifiable claims
        - 1-2: Very poor precision - Extensive hallucinations or fabricated information

        EVALUATION CRITERIA:
        1. Does the answer stick to information that can be verified from the expected content?
        2. Are there any fabricated details, dates, names, or claims not in the reference?
        3. Is all information relevant to the topic and question asked?
        4. Are there any speculative statements presented as facts?

        Return only a single integer score between 1 and 10. 
        """
        self.user_prompt: Template = """
        TASK: Evaluate the information precision and relevance of the generated answer, focusing on detecting hallucinations or fabricated content.

        QUESTION:
        {question}

        EXPECTED ANSWER (Reference):
        {expected_answer}

        GENERATED ANSWER (To Evaluate):
        {generated_answer}

        EVALUATION STEPS:
        1. Compare the generated answer against the reference to identify any added information
        2. Check for fabricated details, names, dates, or claims not present in the reference
        3. Assess whether all information is relevant to the topic
        4. Look for speculative statements presented as definitive facts

        IMPORTANT: Respond with ONLY a single integer from 1 to 10. Do not include any explanation or additional text.
        """


class CompletenessChecker(Checker):
    def __init__(self) -> None:
        super().__init__()
        self.system_prompt = """
        You are a highly precise evaluation assistant specialized in assessing content completeness.

        Your task is to evaluate how completely the generated answer covers the key information from the expected answer.

        SCORING RUBRIC (1-10):
        - 9-10: Comprehensive coverage - All major points and most minor details included
        - 7-8: Good coverage - All major points included, some minor details may be missing
        - 5-6: Adequate coverage - Most major points included, several details missing
        - 3-4: Incomplete coverage - Some major points included, many details missing
        - 1-2: Poor coverage - Few or no major points included

        EVALUATION CRITERIA:
        1. Are all main topics/themes from the expected answer present?
        2. Are supporting details and examples adequately covered?
        3. Is the depth of information comparable to the expected answer?
        4. Are any critical pieces of information missing?

        Return only a single integer score between 1 and 10.
        """
        self.user_prompt = """
        TASK: Evaluate how completely the generated answer covers the content from the expected answer.

        QUESTION:
        {question}

        EXPECTED ANSWER (Reference):
        {expected_answer}

        GENERATED ANSWER (To Evaluate):
        {generated_answer}

        EVALUATION STEPS:
        1. Identify the main topics and key points in the expected answer
        2. Check if each main topic is addressed in the generated answer
        3. Assess the depth and detail level compared to the expected answer
        4. Consider any missing critical information

        IMPORTANT: Respond with ONLY a single integer from 1 to 10. Do not include any explanation or additional text.
        """


class QaEvaluation(BaseModel):
    completeness_score: float = 0.0  # Coverage of expected content
    accuracy_score: float = 0.0  # Factual correctness
    factuality_score: float = 0.0  # Absence of hallucinations
    correct_sources: list[str] = []  # Properly cited sources
    incorrect_sources: list[str] = []  # Incorrectly cited sources
    source_accuracy: float = 0.0  # Precision of source citations
    source_recall: float = (0.0,)  # Recall of expected sources
    levenshtein_score: float = 0.0


class QaEvaluationLogic(
    SingleOutputEvaluationLogic[Input, Output, ExpectedOutput, QaEvaluation]
):

    def __init__(self) -> None:
        super().__init__()
        self.accuracy_checker = AccuracyChecker()
        self.factuality_checker = FactualityChecker()
        self.completeness_checker = CompletenessChecker()

    def do_evaluate_single_output(
        self, example: Example[Input, ExpectedOutput], output: Output
    ) -> QaEvaluation:

        levenshtein_score = difflib.SequenceMatcher(
            None, example.expected_output.sql_query, output.sql_query
        ).ratio()

        completeness_score = self.completeness_checker.get_metric(
            question=example.input.natural_query,
            expected_answer=example.expected_output.sql_query,
            generated_answer=output.sql_query,
        )

        accuracy_score = self.accuracy_checker.get_metric(
            question=example.input.natural_query,
            expected_answer=example.expected_output.sql_query,
            generated_answer=output.sql_query,
        )

        factuality_score = self.factuality_checker.get_metric(
            question=example.input.natural_query,
            expected_answer=example.expected_output.sql_query,
            generated_answer=output.sql_query,
        )

        return QaEvaluation(
            completeness_score=completeness_score,
            accuracy_score=accuracy_score,
            factuality_score=factuality_score,
            levenshtein_score=levenshtein_score,
            # correct_sources=correct_sources,
            # incorrect_sources=incorrect_sources,
            # source_accuracy=self._calculate_source_accuracy(
            #    expected_sources=example.expected_output.sources,
            #    generated_sources=output.sources,
            # ),
            # source_recall=self._calculate_source_recall(
            #    expected_sources=example.expected_output.sources,
            #    generated_sources=output.sources,
            # ),
        )

    def _check_sources(
        self, expected_sources: list[str], generated_sources: list[str]
    ) -> tuple[list[str], list[str]]:
        if not generated_sources:
            return [], []

        if not expected_sources:
            return [], generated_sources.copy()

        expected_set = {source.lower().strip() for source in expected_sources}
        generated_set = {source.lower().strip() for source in generated_sources}

        correct_sources_lower = expected_set.intersection(generated_set)

        correct_sources = []
        incorrect_sources = []

        for source in generated_sources:
            if source.lower().strip() in correct_sources_lower:
                correct_sources.append(source)
            else:
                incorrect_sources.append(source)

        return correct_sources, incorrect_sources

    def _calculate_source_accuracy(
        self, expected_sources: list[str], generated_sources: list[str]
    ) -> float:

        if not generated_sources:
            return 0.0 if expected_sources else 1.0

        correct_sources, _ = self._check_sources(expected_sources, generated_sources)
        return len(correct_sources) / len(generated_sources)

    def _calculate_source_recall(
        self, expected_sources: list[str], generated_sources: list[str]
    ) -> float:
        if not expected_sources:
            return 1.0

        if not generated_sources:
            return 0.0

        expected_set = {source.lower().strip() for source in expected_sources}
        generated_set = {source.lower().strip() for source in generated_sources}

        found_expected = expected_set.intersection(generated_set)
        return len(found_expected) / len(expected_sources)


class QaAggregatedEvaluation(BaseModel):
    average_completeness_score: float
    average_accuracy_score: float
    average_factuality_score: float
    # average_source_accuracy: float
    # average_source_recall: float
    average_levenshtein_score: float


class QaAggregationLogic(
    AggregationLogic[
        QaEvaluation,
        QaAggregatedEvaluation,
    ]
):
    def aggregate(self, evaluations: Iterable[QaEvaluation]) -> QaAggregatedEvaluation:
        evaluation_list = list(evaluations)
        if len(evaluation_list) == 0:
            return QaAggregatedEvaluation(
                average_completeness_score=0.0,
                average_accuracy_score=0.0,
                average_factuality_score=0.0,
                # average_source_accuracy=0.0,
                # average_source_recall=0.0,
                average_levenshtein_score=0.0,
            )

        average_completeness_score = round(
            mean(eval.completeness_score for eval in evaluation_list), 2
        )
        average_accuracy_score = round(
            mean(eval.accuracy_score for eval in evaluation_list), 2
        )
        average_factuality_score = round(
            mean(eval.factuality_score for eval in evaluation_list), 2
        )
        # average_source_accuracy = round(
        #     mean(eval.source_accuracy for eval in evaluation_list), 2
        # )
        # average_source_recall = round(
        #     mean(eval.source_recall for eval in evaluation_list), 2
        # )
        average_levenshtein_score = round(
            mean(eval.levenshtein_score for eval in evaluation_list), 2
        )

        return QaAggregatedEvaluation(
            average_completeness_score=average_completeness_score,
            average_accuracy_score=average_accuracy_score,
            average_factuality_score=average_factuality_score,
            average_levenshtein_score=average_levenshtein_score,
        )
