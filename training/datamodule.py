import os
from glob import glob
from typing import Optional, Sequence, Union

import pytorch_lightning as pl
from datasets.arrow_dataset import Batch, Example
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, BertTokenizer, DataCollatorWithPadding

from datasets import load_dataset, load_from_disk


class DataModule(pl.LightningDataModule):
    label_names = (
        "covid_stats",
        "vaccination",
        "covid_politics",
        "humour",
        "lockdown",
        "civic_views",
        "life_during_pandemic",
        "covid_waves_and_variants",
    )

    tokenizer_keys = ("input_ids", "token_type_ids", "attention_mask")

    def __init__(
        self,
        model_name_or_path: str,
        dataset_path: str,
        batch_size: int,
        fold: Optional[int] = None,
        max_workers: int = os.cpu_count(),
        pin_memory: bool = True,
        use_cache: bool = True,
    ):
        super().__init__()

        self.save_hyperparameters()

        self.num_workers = min(os.cpu_count(), max_workers)

        self.tokenizer: BertTokenizer = AutoTokenizer.from_pretrained(
            model_name_or_path
        )

        self.data_collator = DataCollatorWithPadding(tokenizer=self.tokenizer)

    def setup(self, stage: Optional[str] = None) -> None:
        val_filepath = os.path.join(
            self.hparams.dataset_path, f"fold_{self.hparams.fold}.csv"
        )
        stripped_ds_path = self.hparams.dataset_path.rstrip("/")
        sanitized_model_name = self.hparams.model_name_or_path.replace("/", "_")

        base_save_path = (
            f"{stripped_ds_path}_fold_{self.hparams.fold}_{sanitized_model_name}"
        )

        if stage is None or stage == "fit":
            train_save_path = f"{base_save_path}_train"
            if self.hparams.use_cache and os.path.isdir(train_save_path):
                self.train_ds = load_from_disk(train_save_path)
            else:
                train_files = glob(os.path.join(self.hparams.dataset_path, "*.csv"))
                train_files.remove(val_filepath)

                self.train_ds = self.get_tokenized_ds(train_files)

                if self.hparams.use_cache:
                    self.train_ds.save_to_disk(train_save_path)

        if stage != "predict":
            if self.hparams.use_cache and os.path.isdir(base_save_path):
                self.val_ds = load_from_disk(base_save_path)
            else:
                self.val_ds = self.get_tokenized_ds(val_filepath)

                if self.hparams.use_cache:
                    self.val_ds.save_to_disk(base_save_path)

        if stage is None or stage == "predict":
            if self.hparams.use_cache and os.path.isdir(base_save_path):
                self.pred_ds = load_from_disk(base_save_path)
            else:
                self.pred_ds = self.get_tokenized_ds(self.hparams.dataset_path)

                if self.hparams.use_cache:
                    self.pred_ds.save_to_disk(base_save_path)

    def get_tokenized_ds(
        self,
        data_files: Union[str, Sequence[str]],
    ):
        return (
            load_dataset("csv", data_files=data_files, split="train")
            .map(self.combine_labels, remove_columns=self.label_names)
            .map(self.batched_tokenize, batched=True, batch_size=256)
        )

    @staticmethod
    def combine_labels(row: Example):
        # Not converting to float32 throws an error for loss calculation
        labels = [row[name] for name in DataModule.label_names]
        return {"text": row["text"], "labels": labels}

    def batched_tokenize(self, batched_row: Batch):
        text = batched_row.pop("text")
        tokenized_inputs = self.tokenizer(text, truncation=True)
        return {**batched_row, **tokenized_inputs}

    def train_dataloader(self):
        return DataLoader(
            self.train_ds,
            batch_size=self.hparams.batch_size,
            shuffle=True,
            num_workers=self.num_workers,
            pin_memory=self.hparams.pin_memory,
            collate_fn=self.data_collator,
        )

    def val_dataloader(self):
        return DataLoader(
            self.val_ds,
            batch_size=self.hparams.batch_size,
            num_workers=self.num_workers,
            pin_memory=self.hparams.pin_memory,
            collate_fn=self.data_collator,
        )

    def pred_dataloader(self):
        return DataLoader(
            self.pred_ds,
            batch_size=self.hparams.batch_size,
            num_workers=self.num_workers,
            collate_fn=self.data_collator,
        )
