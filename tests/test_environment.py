"""Basic tests for the Incident Response Environment."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.scenarios import get_scenario, list_tasks, Scenario
from server.graders import EpisodeHistory, grade_episode, check_root_cause, check_remedy
from server.incident_environment import IncidentEnvironment
from models import IncidentAction


def test_list_tasks():
    """Test that all 3 tasks are available."""
    tasks = list_tasks()
    assert len(tasks) == 3
    assert "easy_config_error" in tasks
    assert "medium_cascading_db" in tasks
    assert "hard_intermittent_auth" in tasks
    print("✅ test_list_tasks passed")


def test_scenario_loading():
    """Test that all scenarios load correctly."""
    for task_name in list_tasks():
        scenario = get_scenario(task_name)
        assert isinstance(scenario, Scenario)
        assert scenario.task_name == task_name
        assert len(scenario.services) >= 3
        assert scenario.root_cause != ""
        assert len(scenario.valid_remedies) >= 1
        assert scenario.max_steps > 0
        assert scenario.total_clues > 0
        print(f"  ✅ {task_name}: {len(scenario.services)} services, {scenario.total_clues} clues")
    print("✅ test_scenario_loading passed")


def test_root_cause_check_easy():
    """Test root cause matching for easy scenario."""
    scenario = get_scenario("easy_config_error")

    # Exact match
    exact, partial = check_root_cause(
        "The STRIPE_API_KEY environment variable was misconfigured with an invalid config",
        scenario,
    )
    assert exact, "Should be exact match with multiple keywords"

    # Partial match
    exact, partial = check_root_cause("Something is wrong with the config", scenario)
    assert partial, "Should be partial match with 'config' keyword"

    # No match
    exact, partial = check_root_cause("The database is down", scenario)
    assert not exact and not partial, "Should not match"

    print("✅ test_root_cause_check_easy passed")


def test_remedy_check_easy():
    """Test remedy matching for easy scenario."""
    scenario = get_scenario("easy_config_error")

    # Correct remedy
    attempts = [{"service": "payment-service", "remedy": "rollback_config"}]
    assert check_remedy(attempts, scenario), "Should match valid remedy"

    # Wrong service
    attempts = [{"service": "database", "remedy": "rollback_config"}]
    assert not check_remedy(attempts, scenario), "Wrong service should not match"

    # Wrong remedy
    attempts = [{"service": "payment-service", "remedy": "restart_service"}]
    assert not check_remedy(attempts, scenario), "Wrong remedy should not match"

    print("✅ test_remedy_check_easy passed")


def test_grading_perfect_score():
    """Test that a perfect episode gets a high score."""
    scenario = get_scenario("easy_config_error")

    history = EpisodeHistory(
        root_cause_correct=True,
        root_cause_partial=True,
        remedy_correct=True,
        relevant_clues_found=3,
        steps_used=4,  # Very efficient
    )

    score = grade_episode(scenario, history)
    assert 0.9 <= score <= 1.0, f"Perfect episode should score ~1.0, got {score}"
    print(f"✅ test_grading_perfect_score passed (score: {score})")


def test_grading_no_progress():
    """Test that an empty episode gets a low score."""
    scenario = get_scenario("easy_config_error")

    history = EpisodeHistory(
        steps_used=10,
    )

    score = grade_episode(scenario, history)
    assert score <= 0.1, f"Empty episode should score low, got {score}"
    print(f"✅ test_grading_no_progress passed (score: {score})")


def test_grading_penalties():
    """Test that penalties reduce score."""
    scenario = get_scenario("easy_config_error")

    # Good investigation but wrong remedy
    history = EpisodeHistory(
        root_cause_correct=True,
        remedy_correct=False,
        wrong_remedies=2,
        relevant_clues_found=3,
        steps_used=8,
    )

    score = grade_episode(scenario, history)
    assert score < 0.5, f"Wrong remedies should reduce score significantly, got {score}"
    print(f"✅ test_grading_penalties passed (score: {score})")


def test_grading_difficulty_range():
    """Test that grading works for all 3 difficulty levels."""
    for task_name in list_tasks():
        scenario = get_scenario(task_name)

        # Perfect run
        perfect = EpisodeHistory(
            root_cause_correct=True,
            root_cause_partial=True,
            remedy_correct=True,
            relevant_clues_found=scenario.total_clues,
            steps_used=max(1, scenario.max_steps // 3),
        )
        perfect_score = grade_episode(scenario, perfect)
        assert 0.9 <= perfect_score <= 1.0, f"{task_name} perfect score: {perfect_score}"

        # Failed run
        failed = EpisodeHistory(steps_used=scenario.max_steps)
        failed_score = grade_episode(scenario, failed)
        assert failed_score < 0.1, f"{task_name} failed score: {failed_score}"

        print(f"  ✅ {task_name}: perfect={perfect_score:.2f}, failed={failed_score:.2f}")

    print("✅ test_grading_difficulty_range passed")


def test_score_range():
    """Test that all scores are strictly in (0.0, 1.0)."""
    for task_name in list_tasks():
        scenario = get_scenario(task_name)

        # Test various episode configurations
        configs = [
            EpisodeHistory(),
            EpisodeHistory(root_cause_correct=True, remedy_correct=True, steps_used=1, relevant_clues_found=10),
            EpisodeHistory(wrong_remedies=5, destructive_actions=3, unnecessary_escalations=2, steps_used=20),
        ]

        for history in configs:
            score = grade_episode(scenario, history)
            assert 0.0 < score < 1.0, f"Score {score} out of strict (0.0, 1.0) range"

    print("✅ test_score_range passed")


def test_environment_runtime_rewards_strict_open_interval():
    """Test reset/step runtime rewards are strictly in (0.0, 1.0)."""
    env = IncidentEnvironment()

    obs = env.reset(task_name="easy_config_error")
    assert 0.0 < obs.reward < 1.0, f"Reset reward {obs.reward} not in strict (0.0, 1.0)"

    obs = env.step(IncidentAction(action_type="get_status", target="", parameters={}))
    assert 0.0 < obs.reward < 1.0, f"Neutral step reward {obs.reward} not in strict (0.0, 1.0)"

    obs = env.step(
        IncidentAction(
            action_type="execute_remedy",
            target="",
            parameters={"service": "payment-service", "remedy": "restart_service"},
        )
    )
    assert 0.0 < obs.reward < 1.0, f"Penalty step reward {obs.reward} not in strict (0.0, 1.0)"

    print("✅ test_environment_runtime_rewards_strict_open_interval passed")


def test_episode_return_strict_open_interval():
    """Test that cumulative episode return remains strictly in (0.0, 1.0)."""
    env = IncidentEnvironment()
    rewards = []

    env.reset(task_name="easy_config_error")

    obs = env.step(
        IncidentAction(
            action_type="query_logs",
            target="payment-service",
            parameters={"filter": "error"},
        )
    )
    rewards.append(obs.reward)

    obs = env.step(IncidentAction(action_type="check_metrics", target="payment-service", parameters={}))
    rewards.append(obs.reward)

    obs = env.step(IncidentAction(action_type="read_runbook", target="payment-service", parameters={}))
    rewards.append(obs.reward)

    obs = env.step(
        IncidentAction(
            action_type="identify_root_cause",
            target="",
            parameters={"cause": "misconfigured STRIPE_API_KEY environment variable"},
        )
    )
    rewards.append(obs.reward)

    obs = env.step(
        IncidentAction(
            action_type="execute_remedy",
            target="",
            parameters={"service": "payment-service", "remedy": "rollback_config"},
        )
    )
    rewards.append(obs.reward)
    assert obs.done, "Expected episode to finish after correct remedy"

    total = round(sum(rewards), 4)
    assert 0.0 < total < 1.0, f"Episode return {total} not in strict (0.0, 1.0)"

    print("✅ test_episode_return_strict_open_interval passed")


if __name__ == "__main__":
    print("\n🧪 Running Incident Response Environment Tests\n")
    test_list_tasks()
    test_scenario_loading()
    test_root_cause_check_easy()
    test_remedy_check_easy()
    test_grading_perfect_score()
    test_grading_no_progress()
    test_grading_penalties()
    test_grading_difficulty_range()
    test_score_range()
    test_environment_runtime_rewards_strict_open_interval()
    test_episode_return_strict_open_interval()
    print("\n✅ All tests passed!\n")
