"""
INTUITIVES DAW - Happy Accidents / Parameter Mutation

"Does this sound cool?" - The only rule.

This module provides parameter randomization features to introduce
controlled chaos and serendipity into the music creation process.

Features:
- Mutate: Randomize parameters by a small percentage
- Evolve: Gradually morph parameters over time
- Snapshot: Save/restore random states
- Happy Accidents: Completely random parameter explosions
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Callable
import random
import time
import math

from intlib.log import LOG


# ============================================================================
# MUTATION CONFIGURATION
# ============================================================================

@dataclass
class MutationConfig:
    """Configuration for parameter mutation."""
    # Core settings
    amount: float = 0.05  # Default 5% mutation
    min_amount: float = 0.01  # Minimum 1%
    max_amount: float = 0.50  # Maximum 50%
    
    # Behavior
    bipolar: bool = True  # Can go positive or negative
    respect_bounds: bool = True  # Stay within parameter min/max
    smooth: bool = False  # Apply smoothing over time
    smooth_time_ms: float = 50.0  # Smoothing time in milliseconds
    
    # Probability
    per_param_probability: float = 1.0  # Probability each param gets mutated
    
    # Exclusions
    exclude_volume: bool = True  # Don't mutate volume by default
    exclude_mute: bool = True  # Don't mutate mute/solo
    exclude_pan: bool = False  # Pan can be mutated


@dataclass
class ParameterSnapshot:
    """A snapshot of parameter values for undo/compare."""
    timestamp: float
    parameters: Dict[str, float]
    description: str = ""


# ============================================================================
# MUTATION ENGINE
# ============================================================================

class MutationEngine:
    """
    Happy Accidents Engine - Parameter Mutation and Evolution.
    
    This class provides controlled randomization of audio parameters
    to help discover new sounds through serendipity.
    """
    
    def __init__(
        self,
        config: Optional[MutationConfig] = None,
        on_mutation: Optional[Callable[[str, float, float], None]] = None,
    ):
        """
        PURPOSE: Initializes the Mutation Engine for introducing controlled randomness into project parameters.
        ACTION: Sets the engine's configuration, initializes snapshot history, and resets evolution and statistic trackers.
        MECHANISM: 
            1. Assigns a MutationConfig (or default).
            2. Connects a mutation callback.
            3. Sets up empty dictionaries and lists for snapshot management (undo functionality) and parameter evolution.
        """
        self.config = config or MutationConfig()
        self.on_mutation = on_mutation
        
        # Snapshot history
        self.snapshots: List[ParameterSnapshot] = []
        self.max_snapshots = 50
        
        # Evolution state
        self._evolving = False
        self._evolution_target: Dict[str, float] = {}
        self._evolution_start: Dict[str, float] = {}
        self._evolution_progress = 0.0
        self._evolution_duration = 0.0
        
        # Statistics
        self.total_mutations = 0
        self.total_parameters_mutated = 0
        
        LOG.info("MutationEngine initialized")
    
    def mutate_value(
        self,
        current: float,
        min_val: float = 0.0,
        max_val: float = 1.0,
        amount: Optional[float] = None,
    ) -> float:
        """
        PURPOSE: Modifies a single numerical value based on randomization logic.
        ACTION: Returns a new value that is slightly offset from the original.
        MECHANISM: 
            1. Determines the mutation delta relative to the parameter range.
            2. For bipolar mode, uses a range of [-amount, +amount].
            3. For unipolar mode, uses [0, +amount].
            4. Clamps the result within the specified min/max bounds if config.respect_bounds is True.
        """
        if amount is None:
            amount = self.config.amount
        
        param_range = max_val - min_val
        
        if self.config.bipolar:
            # Bipolar mutation: can go positive or negative
            delta = (random.random() * 2 - 1) * amount * param_range
        else:
            # Unipolar mutation: always increase
            delta = random.random() * amount * param_range
        
        new_value = current + delta
        
        if self.config.respect_bounds:
            new_value = max(min_val, min(max_val, new_value))
        
        return new_value
    
    def mutate_parameters(
        self,
        parameters: Dict[str, float],
        param_info: Optional[Dict[str, Dict[str, float]]] = None,
        amount: Optional[float] = None,
    ) -> Dict[str, float]:
        """
        PURPOSE: Mass-randomizes a set of parameters while respecting exclusion rules.
        ACTION: Iterates through a dictionary of parameters and returns a mutated version.
        MECHANISM: 
            1. Skips parameters matched by _should_skip_param() (e.g. Master Volume).
            2. Applies a per-parameter probability check.
            3. Calls mutate_value() for each qualifying parameter.
            4. Triggers the on_mutation callback to notify the system of changes.
        """
        result = {}
        
        for param_name, current_value in parameters.items():
            # Skip excluded parameters
            if self._should_skip_param(param_name):
                result[param_name] = current_value
                continue
            
            # Apply per-parameter probability
            if random.random() > self.config.per_param_probability:
                result[param_name] = current_value
                continue
            
            # Get bounds
            if param_info and param_name in param_info:
                min_val = param_info[param_name].get('min', 0.0)
                max_val = param_info[param_name].get('max', 1.0)
            else:
                min_val, max_val = 0.0, 1.0
            
            # Mutate
            new_value = self.mutate_value(current_value, min_val, max_val, amount)
            result[param_name] = new_value
            
            # Callback
            if new_value != current_value:
                self.total_parameters_mutated += 1
                if self.on_mutation:
                    try:
                        self.on_mutation(param_name, current_value, new_value)
                    except Exception as e:
                        LOG.warning(f"Mutation callback error: {e}")
        
        self.total_mutations += 1
        return result
    
    def _should_skip_param(self, param_name: str) -> bool:
        """
        PURPOSE: Safety filter to prevent randomization of critical "stability" parameters.
        ACTION: Returns True if the parameter name matches exclusion criteria (like Volume or Mute).
        MECHANISM: Performs case-insensitive substring checks against keywords defined in self.config.
        """
        name_lower = param_name.lower()
        
        if self.config.exclude_volume and 'volume' in name_lower:
            return True
        if self.config.exclude_volume and 'gain' in name_lower:
            return True
        if self.config.exclude_mute and 'mute' in name_lower:
            return True
        if self.config.exclude_mute and 'solo' in name_lower:
            return True
        if self.config.exclude_pan and 'pan' in name_lower:
            return True
        
        return False
    
    def save_snapshot(
        self,
        parameters: Dict[str, float],
        description: str = "",
    ) -> ParameterSnapshot:
        """
        PURPOSE: Captures the current state of parameters to allow for "Undo" or comparison.
        ACTION: Creates a new ParameterSnapshot and adds it to the internal history list.
        MECHANISM: Instantiates the snapshot with a timestamp and a copy of the parameter dictionary, maintaining a max buffer of 50 items.
        """
        snapshot = ParameterSnapshot(
            timestamp=time.time(),
            parameters=parameters.copy(),
            description=description,
        )
        
        self.snapshots.append(snapshot)
        
        # Limit history size
        if len(self.snapshots) > self.max_snapshots:
            self.snapshots = self.snapshots[-self.max_snapshots:]
        
        LOG.debug(f"Saved snapshot: {description or 'unnamed'}")
        return snapshot

    def restore_snapshot(self, index: int = -1) -> Optional[Dict[str, float]]:
        """
        PURPOSE: Reverts parameters to a previously captured state.
        ACTION: Returns a deep copy of the parameter dictionary from the specified snapshot index.
        MECHANISM: Accesses the snapshots list by index and returns the 'parameters' field if it exists.
        """
        if not self.snapshots:
            return None
        
        try:
            snapshot = self.snapshots[index]
            LOG.info(f"Restored snapshot from {snapshot.timestamp}")
            return snapshot.parameters.copy()
        except IndexError:
            return None

    def clear_snapshots(self):
        """
        PURPOSE: Resets the snapshot history.
        ACTION: Empties the internal snapshot list.
        MECHANISM: Calls .clear() on the snapshots list.
        """
        self.snapshots.clear()
    
    # ========================================================================
    # EVOLUTION (Gradual Morphing)
    # ========================================================================
    
    def start_evolution(
        self,
        current_params: Dict[str, float],
        target_params: Optional[Dict[str, float]] = None,
        duration_ms: float = 5000.0,
    ):
        """
        PURPOSE: Initiates a slow, automated morph from one parameter state to another.
        ACTION: Sets the start and target states and starts the evolution timer.
        MECHANISM: 
            1. Copies current parameters to _evolution_start.
            2. Generates random target parameters if none are provided.
            3. Sets the _evolving flag to True.
        """
        self._evolution_start = current_params.copy()
        
        if target_params is None:
            # Generate random targets
            self._evolution_target = self.mutate_parameters(
                current_params,
                amount=0.3  # 30% mutation for targets
            )
        else:
            self._evolution_target = target_params.copy()
        
        self._evolution_duration = duration_ms
        self._evolution_progress = 0.0
        self._evolving = True
        
        LOG.info(f"Started evolution over {duration_ms}ms")

    def stop_evolution(self):
        """
        PURPOSE: Halts any active parameter morphing.
        ACTION: Sets the _evolving flag to False.
        MECHANISM: Direct boolean assignment.
        """
        self._evolving = False
        LOG.info("Evolution stopped")
    
    def update_evolution(self, delta_ms: float) -> Optional[Dict[str, float]]:
        """
        PURPOSE: Calculates the interpolated parameter values for the current point in an evolution sequence.
        ACTION: Returns a dictionary of "in-between" values.
        MECHANISM: 
            1. Calculates progress based on delta_ms.
            2. Applies a 'smoothstep' easing function (3t^2 - 2t^3) for natural transitions.
            3. Linearly interpolates between start and end values using the smoothed progress.
        """
        if not self._evolving:
            return None
        
        self._evolution_progress += delta_ms / self._evolution_duration
        
        if self._evolution_progress >= 1.0:
            self._evolving = False
            return self._evolution_target.copy()
        
        # Smooth interpolation using ease-in-out
        t = self._evolution_progress
        smooth_t = t * t * (3 - 2 * t)  # Smoothstep
        
        result = {}
        for param_name in self._evolution_start:
            start = self._evolution_start[param_name]
            end = self._evolution_target.get(param_name, start)
            result[param_name] = start + (end - start) * smooth_t
        
        return result
    
    @property
    def is_evolving(self) -> bool:
        """
        PURPOSE: External check for evolution status.
        ACTION: Returns the current boolean state of morphing logic.
        MECHANISM: Returns self._evolving.
        """
        return self._evolving
    
    # ========================================================================
    # HAPPY ACCIDENTS (Extreme Randomization)
    # ========================================================================
    
    def happy_accident(
        self,
        parameters: Dict[str, float],
        intensity: float = 0.5,
    ) -> Dict[str, float]:
        """
        PURPOSE: Truncates intentional structure by applying extreme, high-impact randomization.
        ACTION: Returns a dictionary of wildly modified parameters.
        MECHANISM: 
            1. Increases mutation probability and magnitude based on 'intensity'.
            2. Occasionally resets parameters to completely random values (0.0-1.0) instead of relative offsets.
            3. High intensity yields 20-100% mutation ranges.
        """
        LOG.info(f"HAPPY ACCIDENT! Intensity: {intensity:.0%}")
        
        result = {}
        
        for param_name, current_value in parameters.items():
            if self._should_skip_param(param_name):
                result[param_name] = current_value
                continue
            
            # Probability of mutation increases with intensity
            if random.random() > intensity:
                result[param_name] = current_value
                continue
            
            # Large mutations based on intensity
            mutation_amount = 0.2 + (intensity * 0.8)  # 20-100%
            
            # Occasionally go completely random
            if random.random() < intensity * 0.3:
                result[param_name] = random.random()
            else:
                result[param_name] = self.mutate_value(
                    current_value,
                    amount=mutation_amount
                )
        
        self.total_mutations += 1
        return result

    def get_statistics(self) -> Dict[str, Any]:
        """
        PURPOSE: Provides insights into the chaos generated by the engine.
        ACTION: Returns statistical counts and current state descriptions.
        MECHANISM: Returns a dictionary containing mutation counters and evolution progress levels.
        """
        return {
            "total_mutations": self.total_mutations,
            "total_parameters_mutated": self.total_parameters_mutated,
            "snapshots_saved": len(self.snapshots),
            "is_evolving": self._evolving,
            "evolution_progress": f"{self._evolution_progress:.1%}" if self._evolving else "N/A",
        }


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_mutation_engine: Optional[MutationEngine] = None


def get_mutation_engine() -> MutationEngine:
    """
    PURPOSE: Managed access to the global MutationEngine instance.
    ACTION: Returns the active engine, instantiating it lazily if required.
    MECHANISM: Uses a singleton pattern with the _mutation_engine global.
    """
    global _mutation_engine
    if _mutation_engine is None:
        _mutation_engine = MutationEngine()
    return _mutation_engine


def mutate(
    parameters: Dict[str, float],
    amount: float = 0.05,
) -> Dict[str, float]:
    """
    PURPOSE: Lightweight entry point for a single-pass mutation event.
    ACTION: Returns a dictionary of mutated parameters.
    MECHANISM: Calls mutate_parameters() on the global engine instance.
    """
    return get_mutation_engine().mutate_parameters(parameters, amount=amount)


def happy_accident(
    parameters: Dict[str, float],
    intensity: float = 0.5,
) -> Dict[str, float]:
    """
    PURPOSE: Lightweight entry point for triggering a high-intensity "Happy Accident".
    ACTION: Returns a wildly randomized parameter set.
    MECHANISM: Calls happy_accident() on the global engine instance with the specified intensity.
    """
    return get_mutation_engine().happy_accident(parameters, intensity)


# ============================================================================
# MUTATION PRESETS
# ============================================================================

MUTATION_PRESETS = {
    "Subtle": MutationConfig(amount=0.02, per_param_probability=0.3),
    "Gentle": MutationConfig(amount=0.05, per_param_probability=0.5),
    "Medium": MutationConfig(amount=0.10, per_param_probability=0.7),
    "Wild": MutationConfig(amount=0.25, per_param_probability=0.9),
    "Chaos": MutationConfig(amount=0.50, per_param_probability=1.0, exclude_volume=False),
}


def apply_preset(preset_name: str) -> bool:
    """
    PURPOSE: Configures the mutation engine using a named behavioral template (e.g., 'Wild', 'Subtle').
    ACTION: Updates the configuration of the global mutation engine.
    MECHANISM: Looks up the preset name in MUTATION_PRESETS and assigns the corresponding MutationConfig object.
    """
    if preset_name in MUTATION_PRESETS:
        get_mutation_engine().config = MUTATION_PRESETS[preset_name]
        LOG.info(f"Applied mutation preset: {preset_name}")
        return True
    return False
