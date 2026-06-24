"""
Model Evaluation Module
Calculates comprehensive metrics: Accuracy, Precision, Recall, F1-score
"""
import torch
import logging
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from test_set import get_holdout_test_loader

logger = logging.getLogger(__name__)

class ModelEvaluator:
    """Evaluates federated model on central holdout test set"""
    
    @staticmethod
    def evaluate(model, disease='heart', device='cpu'):
        """
        Evaluates model on holdout test set.
        
        Returns:
            dict with accuracy, precision, recall, f1_score, confusion_matrix
        """
        testloader = get_holdout_test_loader(disease=disease)
        model.to(device)
        model.eval()
        
        all_preds = []
        all_targets = []
        total_loss = 0.0
        
        criterion = torch.nn.BCELoss()
        
        with torch.no_grad():
            for data, target in testloader:
                data = data.to(device)
                target = target.to(device)
                
                outputs = model(data)
                loss = criterion(outputs, target.view(-1, 1).float())
                total_loss += loss.item()
                
                # Binary predictions
                predicted = (outputs > 0.5).float().squeeze().cpu().numpy()
                all_preds.extend(predicted)
                all_targets.extend(target.cpu().numpy())
        
        all_preds = [int(p) for p in all_preds]
        all_targets = [int(t) for t in all_targets]
        
        # Calculate metrics
        accuracy = accuracy_score(all_targets, all_preds)
        precision = precision_score(all_targets, all_preds, zero_division=0)
        recall = recall_score(all_targets, all_preds, zero_division=0)
        f1 = f1_score(all_targets, all_preds, zero_division=0)
        tn, fp, fn, tp = confusion_matrix(all_targets, all_preds).ravel()
        
        avg_loss = total_loss / len(testloader) if len(testloader) > 0 else 0.0
        
        metrics = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'loss': float(avg_loss),
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn),
            'true_positives': int(tp),
            'n_samples': len(all_targets)
        }
        
        logger.info(f"Evaluation: Accuracy={accuracy:.4f}, Precision={precision:.4f}, Recall={recall:.4f}, F1={f1:.4f}")
        
        return metrics