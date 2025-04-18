""" evealuation functions for molnextr """
import multiprocessing
import numpy as np
import rdkit
import rdkit.Chem as Chem

rdkit.RDLogger.DisableLog('rdApp.*')
from SmilesPE.pretokenizer import atomwise_tokenizer


def canonicalize_smiles(smiles, ignore_chiral=False, ignore_cistrans=False, replace_rgroup=True):
    """
    Converts a SMILES string to its canonical form, with options to ignore chirality and cis/trans isomerism.

    Args:
        smiles (str): The input SMILES string.
        ignore_chiral (bool): If True, ignores chiral centers in the canonicalization process.
        ignore_cistrans (bool): If True, ignores cis/trans isomerism in the canonicalization.
        replace_rgroup (bool): If True, replaces R-groups in SMILES with a placeholder.

    Returns:
        tuple: Canonical SMILES string and success status (bool).
    """

    if type(smiles) is not str or smiles == '':
        return '', False
    if ignore_cistrans:
        smiles = smiles.replace('/', '').replace('\\', '')
    if replace_rgroup:
        tokens = atomwise_tokenizer(smiles)
        for j, token in enumerate(tokens):
            if token[0] == '[' and token[-1] == ']':
                symbol = token[1:-1]
                if symbol[0] == 'R' and symbol[1:].isdigit():
                    tokens[j] = f'[{symbol[1:]}*]'
                elif Chem.AtomFromSmiles(token) is None:
                    tokens[j] = '*'
        smiles = ''.join(tokens)
    try:
        canon_smiles = Chem.CanonSmiles(smiles, useChiral=(not ignore_chiral))
        success = True
    except:
        canon_smiles = smiles
        success = False
    return canon_smiles, success


def convert_smiles_to_canonsmiles(
        smiles_list, ignore_chiral=False, ignore_cistrans=False, replace_rgroup=True, num_workers=16):
    """
    Converts a list of SMILES strings to their canonical forms in parallel.

    Args:
        smiles_list (list): List of SMILES strings.
        ignore_chiral (bool): If True, ignores chiral centers in the canonicalization.
        ignore_cistrans (bool): If True, ignores cis/trans isomerism in the canonicalization.
        replace_rgroup (bool): If True, replaces R-groups in SMILES with a placeholder.
        num_workers (int): Number of parallel workers to use.

    Returns:
        tuple: List of canonical SMILES and the fraction of successfully converted SMILES.
    """
    with multiprocessing.Pool(num_workers) as p:
        results = p.starmap(canonicalize_smiles,
                            [(smiles, ignore_chiral, ignore_cistrans, replace_rgroup) for smiles in smiles_list],
                            chunksize=128)
    canon_smiles, success = zip(*results)
    return list(canon_smiles), np.mean(success)


class SmilesEvaluator(object):
    """
    Evaluates predicted SMILES strings against gold (true) SMILES strings for canonical equivalence and validity.
    
    Args:
        gold_smiles (list): List of gold (true) SMILES strings.
        num_workers (int): Number of parallel workers to use for SMILES canonicalization.
    """

    def __init__(self, gold_smiles, num_workers=16):
        self.gold_smiles = gold_smiles
        self.gold_canon_smiles, self.gold_valid = convert_smiles_to_canonsmiles(gold_smiles, num_workers=num_workers)
        self.gold_smiles_chiral, _ = convert_smiles_to_canonsmiles(gold_smiles,
                                                                   ignore_chiral=True, num_workers=num_workers)
        self.gold_smiles_cistrans, _ = convert_smiles_to_canonsmiles(gold_smiles,
                                                                     ignore_cistrans=True, num_workers=num_workers)
        self.gold_canon_smiles = self._replace_empty(self.gold_canon_smiles)
        self.gold_smiles_chiral = self._replace_empty(self.gold_smiles_chiral)
        self.gold_smiles_cistrans = self._replace_empty(self.gold_smiles_cistrans)

    def _replace_empty(self, smiles_list):
        """
        Replaces empty or invalid SMILES strings with a placeholder for comparison purposes.

        Args:
            smiles_list (list): List of SMILES strings.

        Returns:
            list: Updated list with placeholders for empty or invalid SMILES.
        """
        return [smiles if smiles is not None and type(smiles) is str and smiles != "" else "<empty>"
                for smiles in smiles_list]

    def evaluate(self, pred_smiles):
        
        """
        Compares predicted SMILES against the gold SMILES based on canonical forms, chirality, and cis/trans isomerism.

        Args:
            pred_smiles (list): List of predicted SMILES strings.

        Returns:
            dict: Evaluation results including accuracy for different levels of canonicalization and chirality.
        """

        results = {}
        results['gold_valid'] = self.gold_valid
        # Canon SMILES
        pred_canon_smiles, pred_valid = convert_smiles_to_canonsmiles(pred_smiles)
        results['canon_smiles_em'] = (np.array(self.gold_canon_smiles) == np.array(pred_canon_smiles)).mean()
        results['pred_valid'] = pred_valid
        # Ignore chirality (Graph exact match)
        pred_smiles_chiral, _ = convert_smiles_to_canonsmiles(pred_smiles, ignore_chiral=True)
        results['graph'] = (np.array(self.gold_smiles_chiral) == np.array(pred_smiles_chiral)).mean()
        # Ignore double bond cis/trans
        pred_smiles_cistrans, _ = convert_smiles_to_canonsmiles(pred_smiles, ignore_cistrans=True)
        results['canon_smiles'] = (np.array(self.gold_smiles_cistrans) == np.array(pred_smiles_cistrans)).mean()
        # Evaluate on molecules with chiral centers
        chiral = np.array([[g, p] for g, p in zip(self.gold_smiles_cistrans, pred_smiles_cistrans) if '@' in g])
        results['chiral_ratio'] = len(chiral) / len(self.gold_smiles)
        results['chiral'] = (chiral[:, 0] == chiral[:, 1]).mean() if len(chiral) > 0 else -1
        return results
