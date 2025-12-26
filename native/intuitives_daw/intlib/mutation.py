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
        Initialize the Mutation Engine.
        
        Args:
            config: Mutation configuration
            on_mutation: Callback(param_name, old_value, new_value) on mutation
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
        Mutate a single value within bounds.
        
        Args:
            current: Current parameter value
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            amount: Mutation amount (0-1), or None for config default
            
        Returns:
            New mutated value
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
        Mutate a dictionary of parameters.
        
        Args:
            parameters: Dict of parameter_name -> current_value
            param_info: Optional dict with min/max for each param
            amount: Mutation amount override
            
        Returns:
            Dict of parameter_name -> new_value
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
        """Check if a parameter should be skipped based on config."""
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
        """Save a parameter snapshot for undo/compare."""
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
        """Restore a parameter snapshot by index (default: last)."""
        if not self.snapshots:
            return None
        
        try:
            snapshot = self.snapshots[index]
            LOG.info(f"Restored snapshot from {snapshot.timestamp}")
            return snapshot.parameters.copy()
        except IndexError:
            return None
    
    def clear_snapshots(self):
        """Clear all snapshots."""
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
        Start evolving parameters toward a target over time.
        
        Args:
            current_params: Current parameter values
            target_params: Target values (None = random)
            duration_ms: Evolution duration in milliseconds
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
        """Stop the evolution process."""
        self._evolving = False
        LOG.info("Evolution stopped")
    
    def update_evolution(self, delta_ms: float) -> Optional[Dict[str, float]]:
        """
        Update evolution progress and return interpolated parameters.
        
        Args:
            delta_ms: Time elapsed since last update in milliseconds
            
        Returns:
            Interpolated parameters, or None if not evolving
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
        """Check if evolution is in progress."""
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
        Trigger a "Happy Accident" - extreme randomization.
        
        This is for when you want to completely break out of your
        current sound and discover something new.
        
        Args:
            parameters: Current parameter values
            intensity: 0.0-1.0, how extreme the changes are
            
        Returns:
            Wildly mutated parameters
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
        """Get mutation statistics."""
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
    """Get the global MutationEngine instance."""
    global _mutation_engine
    if _mutation_engine is None:
        _mutation_engine = MutationEngine()
    return _mutation_engine


def mutate(
    parameters: Dict[str, float],
    amount: float = 0.05,
) -> Dict[str, float]:
    """Quick mutation of parameters."""
    return get_mutation_engine().mutate_parameters(parameters, amount=amount)


def happy_accident(
    parameters: Dict[str, float],
    intensity: float = 0.5,
) -> Dict[str, float]:
    """Trigger a happy accident."""
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
    """Apply a mutation preset."""
    if preset_name in MUTATION_PRESETS:
        get_mutation_engine().config = MUTATION_PRESETS[preset_name]
        LOG.info(f"Applied mutation preset: {preset_name}")
        return True
    return False
