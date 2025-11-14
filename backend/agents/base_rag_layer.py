"""
Stage 1: Base RAG Layer - Database-Powered Knowledge Retrieval
This stage uses existing implemented pipelines to create BaseContext
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..services.member1.options_flow_service import OptionsFlowService
from ..services.member2.explain_move_service import ExplainMoveService
from ..services.member3.macro_gap_service import MacroGapService
from ..rag_engine.llm_manager import LLMManager
from ..db.postgres_handler import PostgresHandler

logger = logging.getLogger(__name__)

class BaseRAGLayer:
    """
    Stage 1: Database-powered RAG layer
    Uses existing implemented services to retrieve all internal knowledge
    """
    
    def __init__(self):
        self.options_service = OptionsFlowService()
        self.move_service = ExplainMoveService()
        self.macro_service = MacroGapService()
        self.llm_manager = LLMManager()
        self.db = PostgresHandler()
        
        logger.info("BaseRAGLayer initialized with all 4 LLM modules")
    
    async def route_query(self, query: str, ticker: Optional[str] = None, 
                         timestamp: Optional[datetime] = None) -> Dict[str, str]:
        """
        Router Node: Determine which modules should be activated
        
        Returns:
            Dict with activated modules and routing confidence
        """
        routing = {
            'risk': False,
            'options': False,
            'move_explainer': False,
            'macro_gap': False,
            'routing_confidence': 0.0
        }
        
        query_lower = query.lower()
        confidence_score = 0.0
        
        # Risk module triggers
        if any(word in query_lower for word in [
            'risk', 'danger', 'threat', 'volatile', 'uncertainty', 'concern',
            'exposure', 'downside', 'upside', 'assessment', 'factors'
        ]):
            routing['risk'] = True
            confidence_score += 0.25
            
        # Options module triggers  
        if any(word in query_lower for word in [
            'options', 'calls', 'puts', 'flow', 'unusual', 'activity',
            'institutional', 'whale', 'volume', 'iv', 'implied volatility'
        ]):
            routing['options'] = True
            confidence_score += 0.25
            
        # Move explainer triggers
        if any(word in query_lower for word in [
            'move', 'drop', 'spike', 'jump', 'crash', 'surge', 'movement',
            'explain', 'why', 'happened', 'cause', 'reason', 'sudden'
        ]) or timestamp is not None:
            routing['move_explainer'] = True
            confidence_score += 0.25
            
        # Macro gap triggers
        if any(word in query_lower for word in [
            'gap', 'tomorrow', 'overnight', 'premarket', 'aftermarket',
            'fed', 'fomc', 'macro', 'earnings', 'announcement', 'forecast'
        ]):
            routing['macro_gap'] = True
            confidence_score += 0.25
            
        # Default to risk if nothing specific detected
        if not any([routing['risk'], routing['options'], routing['move_explainer'], routing['macro_gap']]):
            routing['risk'] = True
            confidence_score = 0.5
            
        routing['routing_confidence'] = min(confidence_score, 1.0)
        
        logger.info(f"Query routed to modules: {[k for k,v in routing.items() if v and k != 'routing_confidence']}")
        return routing
    
    async def execute_base_rag(self, query: str, ticker: str, 
                              timestamp: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Execute Base RAG across all relevant modules
        
        Returns:
            BaseContext with all internal knowledge
        """
        try:
            # Route the query
            routing = await self.route_query(query, ticker, timestamp)
            
            base_context = {
                'query': query,
                'ticker': ticker,
                'timestamp': timestamp.isoformat() if timestamp else None,
                'routing': routing,
                'modules_executed': [],
                'db_insights': {},
                'evidence_summary': {},
                'base_confidence': 0.0
            }
            
            total_confidence = 0.0
            modules_count = 0
            
            # Execute Risk Assessment if routed
            if routing.get('risk', False):
                try:
                    # Create risk assessment using existing chat-style approach
                    system_prompt = """You are a financial risk analyst AI assistant. 
                    Analyze the user's question and provide helpful insights about financial risks, 
                    market conditions, and investment considerations. 
                    Be concise, factual, and avoid giving specific trading advice."""
                    
                    llm_response = await self.llm_manager.generate(
                        prompt=f"Risk assessment for {ticker}: {query}",
                        system_prompt=system_prompt
                    )
                    
                    risk_result = {
                        'answer': llm_response,
                        'confidence': 0.8,
                        'evidence': [{
                            'source': 'llm_analysis',
                            'snippet': 'Risk analysis based on general market knowledge',
                            'timestamp': datetime.now().isoformat()
                        }],
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    base_context['modules_executed'].append('risk')
                    base_context['db_insights']['risk'] = risk_result
                    total_confidence += risk_result.get('confidence', 0.5)
                    modules_count += 1
                    logger.info("Risk module executed successfully")
                except Exception as e:
                    logger.error(f"Risk module execution failed: {e}")
            
            # Execute Options Flow if routed
            if routing.get('options', False):
                try:
                    options_result = await self.options_service.analyze_flow(
                        ticker=ticker,
                        user_question=query
                    )
                    base_context['modules_executed'].append('options')
                    base_context['db_insights']['options'] = options_result
                    total_confidence += options_result.get('confidence', 0.5)
                    modules_count += 1
                    logger.info("Options flow module executed successfully")
                except Exception as e:
                    logger.error(f"Options flow module execution failed: {e}")
            
            # Execute Move Explainer if routed
            if routing.get('move_explainer', False):
                try:
                    move_timestamp = timestamp or datetime.now()
                    move_result = await self.move_service.analyze_movement(
                        ticker=ticker,
                        timestamp=move_timestamp
                    )
                    base_context['modules_executed'].append('move_explainer')
                    base_context['db_insights']['move_explainer'] = move_result
                    total_confidence += move_result.get('confidence', 0.5)
                    modules_count += 1
                    logger.info("Move explainer module executed successfully")
                except Exception as e:
                    logger.error(f"Move explainer module execution failed: {e}")
            
            # Execute Macro Gap if routed
            if routing.get('macro_gap', False):
                try:
                    gap_result = await self.macro_service.predict_gap(
                        asset=ticker,
                        question=query
                    )
                    base_context['modules_executed'].append('macro_gap')
                    base_context['db_insights']['macro_gap'] = gap_result
                    total_confidence += gap_result.get('confidence', 0.5)
                    modules_count += 1
                    logger.info("Macro gap module executed successfully")
                except Exception as e:
                    logger.error(f"Macro gap module execution failed: {e}")
            
            # Calculate overall base confidence
            if modules_count > 0:
                base_context['base_confidence'] = total_confidence / modules_count
            else:
                base_context['base_confidence'] = 0.0
            
            # Create evidence summary
            base_context['evidence_summary'] = self._summarize_evidence(base_context['db_insights'])
            
            logger.info(f"Base RAG completed. Modules: {base_context['modules_executed']}, Confidence: {base_context['base_confidence']:.2f}")
            
            return base_context
            
        except Exception as e:
            logger.error(f"Base RAG execution failed: {e}")
            return {
                'query': query,
                'ticker': ticker,
                'timestamp': timestamp.isoformat() if timestamp else None,
                'routing': {'error': str(e)},
                'modules_executed': [],
                'db_insights': {},
                'evidence_summary': {},
                'base_confidence': 0.0,
                'error': str(e)
            }
    
    def _summarize_evidence(self, db_insights: Dict[str, Any]) -> Dict[str, Any]:
        """
        Summarize evidence from all executed modules
        """
        summary = {
            'total_evidence_chunks': 0,
            'evidence_types': set(),
            'confidence_range': [1.0, 0.0],  # [min, max]
            'key_findings': []
        }
        
        for module, result in db_insights.items():
            if isinstance(result, dict):
                # Count evidence
                evidence = result.get('evidence', [])
                if isinstance(evidence, list):
                    summary['total_evidence_chunks'] += len(evidence)
                elif isinstance(evidence, dict):
                    # For nested evidence structures
                    for key, value in evidence.items():
                        if isinstance(value, list):
                            summary['total_evidence_chunks'] += len(value)
                
                # Track confidence range
                conf = result.get('confidence', 0.5)
                if conf < summary['confidence_range'][0]:
                    summary['confidence_range'][0] = conf
                if conf > summary['confidence_range'][1]:
                    summary['confidence_range'][1] = conf
                
                # Extract key findings
                if module == 'risk':
                    summary['key_findings'].append(f"Risk: {result.get('answer', 'Analysis completed')[:100]}")
                elif module == 'options':
                    summary['key_findings'].append(f"Options: {result.get('insight', 'Analysis completed')[:100]}")
                elif module == 'move_explainer':
                    summary['key_findings'].append(f"Movement: {result.get('summary', 'Analysis completed')[:100]}")
                elif module == 'macro_gap':
                    summary['key_findings'].append(f"Gap Forecast: {result.get('gap_prediction', 'Analysis completed')[:100]}")
        
        summary['evidence_types'] = list(summary['evidence_types'])
        
        return summary
