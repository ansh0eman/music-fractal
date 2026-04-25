"""
Lyrics analysis and feature extraction.

Extracts structural patterns, repetition, symmetry, and other features
from song lyrics for fractal parameter mapping.
"""
import re
from typing import List, Dict, Tuple
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class LyricsAnalyzer:
    """Analyzes lyrics and extracts features for fractal generation."""

    # Common stop words (can be expanded)
    STOP_WORDS = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
        "been", "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "could", "should", "may", "might", "must", "can", "this",
        "that", "these", "those", "i", "you", "he", "she", "it", "we", "they",
        "me", "him", "her", "us", "them", "my", "your", "his", "her", "its",
        "our", "their", "what", "which", "who", "whom", "whose", "where",
        "when", "why", "how", "all", "each", "every", "both", "few", "more",
        "most", "other", "some", "such", "no", "nor", "not", "only", "own",
        "same", "so", "than", "too", "very", "just", "now"
    }

    def preprocess(self, lyrics: str, remove_stop_words: bool = False) -> List[str]:
        """
        Preprocess lyrics: normalize, tokenize, segment.

        Args:
            lyrics: Raw lyrics text
            remove_stop_words: Whether to filter out stop words

        Returns:
            List of lines (each line is a string of tokens)
        """
        # Normalize: lowercase, remove extra whitespace
        text = lyrics.lower().strip()
        
        # Remove common annotations like [Verse], [Chorus], etc.
        text = re.sub(r'\[.*?\]', '', text)
        
        # Split into lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if remove_stop_words:
            processed_lines = []
            for line in lines:
                tokens = re.findall(r'\b\w+\b', line)
                filtered = [t for t in tokens if t not in self.STOP_WORDS]
                processed_lines.append(' '.join(filtered))
            return processed_lines
        
        return lines

    def estimate_syllables(self, word: str) -> int:
        """
        Simple syllable estimation using vowel counting.

        This is a heuristic and not perfect, but sufficient for our purposes.
        """
        word = word.lower().strip()
        if not word:
            return 1
        
        # Count vowel groups
        vowels = re.findall(r'[aeiouy]+', word)
        syllable_count = len(vowels)
        
        # Adjust for silent e
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        # Minimum 1 syllable
        return max(1, syllable_count)

    def extract_features(self, lyrics: str) -> Dict[str, float]:
        """
        Extract comprehensive features from lyrics.

        Returns:
            Dictionary of feature names to normalized values (0-1 range where applicable)
        """
        lines = self.preprocess(lyrics, remove_stop_words=False)
        
        if not lines:
            return self._default_features()

        # Line length statistics
        line_lengths = [len(line.split()) for line in lines]
        char_lengths = [len(line) for line in lines]
        
        # Syllable counts per line
        syllable_counts = []
        for line in lines:
            words = re.findall(r'\b\w+\b', line.lower())
            syllables = sum(self.estimate_syllables(w) for w in words)
            syllable_counts.append(syllables)

        # Repetition analysis
        repetition_score = self._compute_repetition_score(lines)
        
        # N-gram analysis
        ngram_diversity = self._compute_ngram_diversity(lines)
        
        # Structural symmetry (verse/chorus patterns)
        symmetry_score = self._compute_symmetry_score(lines)
        
        # Line length variance (for angular distortion mapping)
        line_length_variance = self._variance(line_lengths) if line_lengths else 0.0
        syllable_variance = self._variance(syllable_counts) if syllable_counts else 0.0

        # Normalize features to 0-1 range where appropriate
        features = {
            "repetition_score": min(1.0, repetition_score),
            "symmetry_score": min(1.0, symmetry_score),
            "ngram_diversity": min(1.0, ngram_diversity),
            "line_length_mean": sum(line_lengths) / len(line_lengths) if line_lengths else 0.0,
            "line_length_variance": min(1.0, line_length_variance / 100.0),  # Normalize
            "syllable_variance": min(1.0, syllable_variance / 50.0),  # Normalize
            "num_lines": len(lines),
            "avg_chars_per_line": sum(char_lengths) / len(char_lengths) if char_lengths else 0.0,
        }

        logger.info(f"Extracted features: {features}")
        return features

    def _compute_repetition_score(self, lines: List[str]) -> float:
        """Compute how repetitive the lyrics are (0-1, higher = more repetitive)."""
        if len(lines) < 2:
            return 0.0

        # Count exact line repetitions
        line_counts = Counter(lines)
        repeated_lines = sum(1 for count in line_counts.values() if count > 1)
        
        # Also check for similar lines (fuzzy matching)
        total_repetitions = sum(count - 1 for count in line_counts.values() if count > 1)
        
        # Normalize by total unique lines
        unique_lines = len(line_counts)
        if unique_lines == 0:
            return 0.0
        
        score = min(1.0, (total_repetitions / max(1, unique_lines)) * 0.5)
        
        # Boost if there are many repeated lines
        if repeated_lines > len(lines) * 0.3:
            score = min(1.0, score + 0.3)
        
        return score

    def _compute_ngram_diversity(self, lines: List[str], n: int = 3) -> float:
        """
        Compute n-gram diversity (lower = more repetitive, higher = more diverse).
        Returns normalized score (0-1, higher = more diverse).
        """
        if not lines:
            return 0.0

        all_ngrams = []
        for line in lines:
            tokens = re.findall(r'\b\w+\b', line.lower())
            for i in range(len(tokens) - n + 1):
                ngram = tuple(tokens[i:i+n])
                all_ngrams.append(ngram)

        if not all_ngrams:
            return 0.0

        unique_ngrams = len(set(all_ngrams))
        total_ngrams = len(all_ngrams)
        
        # Diversity = unique / total (higher = more diverse)
        diversity = unique_ngrams / total_ngrams if total_ngrams > 0 else 0.0
        return diversity

    def _compute_symmetry_score(self, lines: List[str]) -> float:
        """
        Detect structural symmetry (verse/chorus patterns).
        Returns score 0-1 (higher = more symmetric structure).
        """
        if len(lines) < 4:
            return 0.0

        # Simple heuristic: check if first and last sections are similar
        # or if there are repeated blocks
        
        # Compare first quarter with last quarter
        quarter = len(lines) // 4
        if quarter > 0:
            first_quarter = lines[:quarter]
            last_quarter = lines[-quarter:]
            
            # Count matching lines
            matches = sum(1 for f, l in zip(first_quarter, last_quarter) if f == l)
            symmetry = matches / quarter if quarter > 0 else 0.0
            
            # Also check for repeated blocks in the middle
            # Look for 2+ consecutive repeated lines
            consecutive_repeats = 0
            for i in range(len(lines) - 1):
                if lines[i] == lines[i + 1]:
                    consecutive_repeats += 1
            
            block_symmetry = min(1.0, consecutive_repeats / len(lines))
            
            return min(1.0, (symmetry * 0.6 + block_symmetry * 0.4))
        
        return 0.0

    def _variance(self, values: List[float]) -> float:
        """Compute variance of a list of values."""
        if not values or len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / len(values)

    def _default_features(self) -> Dict[str, float]:
        """Return default feature values when lyrics are unavailable."""
        return {
            "repetition_score": 0.0,
            "symmetry_score": 0.0,
            "ngram_diversity": 0.5,
            "line_length_mean": 0.0,
            "line_length_variance": 0.0,
            "syllable_variance": 0.0,
            "num_lines": 0,
            "avg_chars_per_line": 0.0,
        }
