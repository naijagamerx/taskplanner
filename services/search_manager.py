#!/usr/bin/env python3
"""
Global Search Manager for Task Planner
Provides comprehensive search functionality across all data types
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date
from models.task import Task
from models.category import Category
from models.goal import Goal
from database.settings_manager import SettingsManager

class SearchResult:
    """Represents a search result item"""
    
    def __init__(self, item_type: str, item_id: int, title: str, description: str = "",
                 match_score: float = 0.0, match_highlights: List[str] = None,
                 metadata: Dict[str, Any] = None):
        self.item_type = item_type  # 'task', 'goal', 'category', 'habit'
        self.item_id = item_id
        self.title = title
        self.description = description
        self.match_score = match_score
        self.match_highlights = match_highlights or []
        self.metadata = metadata or {}
        self.timestamp = datetime.now()

class SearchManager:
    """Advanced search functionality across all application data"""
    
    def __init__(self):
        self.settings = SettingsManager()
        self.search_history = []
        self.max_history = 50
        
        # Search configuration
        self.search_config = {
            'fuzzy_matching': True,
            'case_sensitive': False,
            'whole_words_only': False,
            'include_completed': True,
            'include_archived': False,
            'max_results': 100,
            'min_score_threshold': 0.1
        }
        
        # Load search settings
        self.load_search_settings()
    
    def load_search_settings(self):
        """Load search configuration from settings"""
        try:
            saved_config = self.settings.get('search_config', {})
            self.search_config.update(saved_config)
        except Exception as e:
            print(f"Error loading search settings: {e}")
    
    def save_search_settings(self):
        """Save search configuration to settings"""
        try:
            self.settings.set('search_config', self.search_config)
            self.settings.save()
        except Exception as e:
            print(f"Error saving search settings: {e}")
    
    def global_search(self, query: str, filters: Dict[str, Any] = None) -> List[SearchResult]:
        """Perform global search across all data types"""
        if not query or len(query.strip()) < 2:
            return []
        
        query = query.strip()
        filters = filters or {}
        results = []
        
        try:
            # Add to search history
            self.add_to_history(query)
            
            # Search tasks
            if filters.get('include_tasks', True):
                task_results = self.search_tasks(query)
                results.extend(task_results)
            
            # Search goals
            if filters.get('include_goals', True):
                goal_results = self.search_goals(query)
                results.extend(goal_results)
            
            # Search categories
            if filters.get('include_categories', True):
                category_results = self.search_categories(query)
                results.extend(category_results)
            
            # Search habits (if available)
            if filters.get('include_habits', True):
                habit_results = self.search_habits(query)
                results.extend(habit_results)
            
            # Sort by relevance score
            results.sort(key=lambda x: x.match_score, reverse=True)
            
            # Apply result limit
            max_results = filters.get('max_results', self.search_config['max_results'])
            results = results[:max_results]
            
            print(f"🔍 Global search for '{query}' returned {len(results)} results")
            return results
            
        except Exception as e:
            print(f"Error in global search: {e}")
            return []
    
    def search_tasks(self, query: str) -> List[SearchResult]:
        """Search tasks with advanced matching"""
        results = []
        
        try:
            # Get all tasks
            all_tasks = Task.get_all()
            
            for task in all_tasks:
                # Skip completed tasks if configured
                if not self.search_config['include_completed'] and task.status == 'completed':
                    continue
                
                # Calculate match score
                score, highlights = self.calculate_match_score(
                    query, task.title, task.description or ""
                )
                
                if score >= self.search_config['min_score_threshold']:
                    # Get additional metadata
                    metadata = {
                        'status': task.status,
                        'priority_id': task.priority_id,
                        'category_id': task.category_id,
                        'due_date': task.due_date.isoformat() if task.due_date else None,
                        'created_at': task.created_at.isoformat() if task.created_at else None
                    }
                    
                    result = SearchResult(
                        item_type='task',
                        item_id=task.id,
                        title=task.title,
                        description=task.description or "",
                        match_score=score,
                        match_highlights=highlights,
                        metadata=metadata
                    )
                    results.append(result)
            
        except Exception as e:
            print(f"Error searching tasks: {e}")
        
        return results
    
    def search_goals(self, query: str) -> List[SearchResult]:
        """Search goals"""
        results = []
        
        try:
            all_goals = Goal.get_all()
            
            for goal in all_goals:
                score, highlights = self.calculate_match_score(
                    query, goal.title, goal.description or ""
                )
                
                if score >= self.search_config['min_score_threshold']:
                    metadata = {
                        'status': goal.status,
                        'progress_percentage': goal.progress_percentage,
                        'target_date': goal.target_date.isoformat() if goal.target_date else None
                    }
                    
                    result = SearchResult(
                        item_type='goal',
                        item_id=goal.id,
                        title=goal.title,
                        description=goal.description or "",
                        match_score=score,
                        match_highlights=highlights,
                        metadata=metadata
                    )
                    results.append(result)
            
        except Exception as e:
            print(f"Error searching goals: {e}")
        
        return results
    
    def search_categories(self, query: str) -> List[SearchResult]:
        """Search categories"""
        results = []
        
        try:
            all_categories = Category.get_all()
            
            for category in all_categories:
                score, highlights = self.calculate_match_score(
                    query, category.name, category.description or ""
                )
                
                if score >= self.search_config['min_score_threshold']:
                    metadata = {
                        'color': category.color,
                        'task_count': len(Task.get_by_category(category.id))
                    }
                    
                    result = SearchResult(
                        item_type='category',
                        item_id=category.id,
                        title=category.name,
                        description=category.description or "",
                        match_score=score,
                        match_highlights=highlights,
                        metadata=metadata
                    )
                    results.append(result)
            
        except Exception as e:
            print(f"Error searching categories: {e}")
        
        return results
    
    def search_habits(self, query: str) -> List[SearchResult]:
        """Search habits (placeholder for future implementation)"""
        results = []
        # TODO: Implement habit search when habit model is available
        return results
    
    def calculate_match_score(self, query: str, title: str, description: str) -> Tuple[float, List[str]]:
        """Calculate relevance score and highlights for a search match"""
        query_lower = query.lower() if not self.search_config['case_sensitive'] else query
        title_lower = title.lower() if not self.search_config['case_sensitive'] else title
        desc_lower = description.lower() if not self.search_config['case_sensitive'] else description
        
        score = 0.0
        highlights = []
        
        # Exact title match (highest score)
        if query_lower == title_lower:
            score += 1.0
            highlights.append(f"Exact title match: '{title}'")
        
        # Title starts with query
        elif title_lower.startswith(query_lower):
            score += 0.8
            highlights.append(f"Title starts with: '{query}'")
        
        # Title contains query
        elif query_lower in title_lower:
            score += 0.6
            highlights.append(f"Title contains: '{query}'")
        
        # Description contains query
        if query_lower in desc_lower:
            score += 0.3
            highlights.append(f"Description contains: '{query}'")
        
        # Fuzzy matching for partial words
        if self.search_config['fuzzy_matching']:
            fuzzy_score = self.fuzzy_match(query_lower, title_lower + " " + desc_lower)
            score += fuzzy_score * 0.2
        
        # Word boundary matching
        if self.search_config['whole_words_only']:
            word_pattern = r'\b' + re.escape(query_lower) + r'\b'
            if re.search(word_pattern, title_lower):
                score += 0.4
            if re.search(word_pattern, desc_lower):
                score += 0.2
        
        return min(score, 1.0), highlights
    
    def fuzzy_match(self, query: str, text: str) -> float:
        """Simple fuzzy matching algorithm"""
        if not query or not text:
            return 0.0
        
        # Simple character-based fuzzy matching
        matches = 0
        query_pos = 0
        
        for char in text:
            if query_pos < len(query) and char == query[query_pos]:
                matches += 1
                query_pos += 1
        
        return matches / len(query) if len(query) > 0 else 0.0
    
    def add_to_history(self, query: str):
        """Add search query to history"""
        try:
            # Remove if already exists
            if query in self.search_history:
                self.search_history.remove(query)
            
            # Add to beginning
            self.search_history.insert(0, query)
            
            # Limit history size
            if len(self.search_history) > self.max_history:
                self.search_history = self.search_history[:self.max_history]
            
            # Save to settings
            self.settings.set('search_history', self.search_history)
            self.settings.save()
            
        except Exception as e:
            print(f"Error adding to search history: {e}")
    
    def get_search_history(self) -> List[str]:
        """Get search history"""
        try:
            saved_history = self.settings.get('search_history', [])
            self.search_history = saved_history
            return self.search_history
        except Exception as e:
            print(f"Error getting search history: {e}")
            return []
    
    def clear_search_history(self):
        """Clear search history"""
        try:
            self.search_history = []
            self.settings.set('search_history', [])
            self.settings.save()
        except Exception as e:
            print(f"Error clearing search history: {e}")
    
    def get_search_suggestions(self, partial_query: str) -> List[str]:
        """Get search suggestions based on partial query"""
        suggestions = []
        
        try:
            # Get from history
            history_suggestions = [
                h for h in self.search_history 
                if h.lower().startswith(partial_query.lower())
            ][:5]
            suggestions.extend(history_suggestions)
            
            # Get from task titles
            if len(suggestions) < 10:
                tasks = Task.get_all()
                task_suggestions = [
                    task.title for task in tasks 
                    if task.title.lower().startswith(partial_query.lower())
                ][:5]
                suggestions.extend(task_suggestions)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_suggestions = []
            for item in suggestions:
                if item not in seen:
                    seen.add(item)
                    unique_suggestions.append(item)
            
            return unique_suggestions[:10]
            
        except Exception as e:
            print(f"Error getting search suggestions: {e}")
            return []

# Global search manager instance
search_manager = SearchManager()
