import zlib

import base64
import json
import logging
import os
from tqdm import tqdm
from typing import Optional, Any, Dict, List, Text

from rasa_core import utils
from rasa_core.domain import Domain
from rasa_core.events import ActionExecuted, SlotSet
from rasa_core.featurizers import (
    TrackerFeaturizer, MaxHistoryTrackerFeaturizer)
from rasa_core.policies.policy import Policy
from rasa_core.trackers import DialogueStateTracker
from rasa_core.actions.action import ACTION_LISTEN_NAME


logger = logging.getLogger(__name__)


class BottisPolicy(Policy):
    def __init__(self,
                 priority: int = 2,
                 nlu_threshold: float = 0.7,
                 core_threshold: float = 0.7,
                 custom_response_action_name: Text = "action_custom_response",
                 featurizer: Optional[TrackerFeaturizer] = None,
                 max_history: Optional[int] = None,
                 lookup: Optional[Dict] = None
                 ) -> None:

        self.custom_response_action_name = custom_response_action_name
        self.core_threshold = core_threshold
        self.nlu_threshold = nlu_threshold
        self.priority = priority
        super(BottisPolicy, self).__init__(featurizer, priority)

    def train(self,
              training_trackers: List[DialogueStateTracker],
              domain: Domain,
              **kwargs: Any
              ) -> None:
        """Pretending to train the bots policy."""

        logger.warning("Olaaaa, estou treinando genteee")

    def bottis_score(self, result, domain, bottis_score=1.0):
        idx = domain.index_for_action(self.custom_response_action_name)
        result[idx] = self.core_threshold

        return result

    def predict_action_probabilities(self,
                                     tracker: DialogueStateTracker,
                                     domain: Domain) -> List[float]:
        """Predicts the next action the bot should take
        after seeing the tracker.

        Returns the list of probabilities for the next actions"""

        #text = tracker.latest_message.get('text')

        # TODO: Inserção das API's sem ser hardcode
        # bots = ["localhost:5006", 'localhost:5007']

        # TODO: Paralelizar o envio das mensagens para as APIs cadastradas
        # TODO: Configurar os dados que recebemos do tracker em uma struct separada
        result = [0.0] * domain.num_actions

        if tracker.latest_action_name == self.custom_response_action_name:
            result = [0.0] * domain.num_actions
            idx = domain.index_for_action(ACTION_LISTEN_NAME)
            result[idx] = 1.0
        elif tracker.latest_message.intent.get('name') == None and \
             tracker.latest_message.intent.get('confidence') < self.nlu_threshold:
            set_answer_slot_event = SlotSet("bot_answer", "Chegou na policy")
            tracker.update(set_answer_slot_event)

            result = self.bottis_score(result, domain, self.core_threshold)

        return result

    def persist(self, path: Text) -> None:
        """Persists the policy to storage."""
    
        config_file = os.path.join(path, 'bottis_policy.json')
        meta = {
                "priority": self.priority,
                "nlu_threshold": self.nlu_threshold,
                "core_threshold": self.core_threshold,
                "custom_response_action_name": self.custom_response_action_name
                }
        utils.create_dir_for_file(config_file)
        utils.dump_obj_as_json_to_file(config_file, meta)

    @classmethod
    def load(cls, path: Text) -> 'BottisPolicy':
        meta = {}
        if os.path.exists(path):
            meta_path = os.path.join(path, "bottis_policy.json")
            if os.path.isfile(meta_path):
                meta = json.loads(utils.read_file(meta_path))

        return cls(**meta)
