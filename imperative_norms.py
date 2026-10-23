class ImperativeNormGuard:
    """
    Императивная норма: Процедура НИКОГДА не может обнулять ФАКТ.
    Это жесткий запрет, который выбрасывает RuntimeError на уровне ядра.
    """
    @staticmethod
    def enforce(new_node, existing_nodes):
        if new_node.node_type == "PROCEDURE":
            # Ищем, не пытается ли процедура обнулить факт, на который ссылается
            target_fact = existing_nodes.get(new_node.parent_hash)
            
            if target_fact and target_fact.node_type == "FACT":
                # Если процедура содержит маркеры обнуления/отмены
                if any(marker in new_node.fact_data.lower() for marker in ["обнулить", "invalid", "отменить"]):
                    raise RuntimeError(
                        f"IMPERATIVE NORM VIOLATION: Процедура {new_node.node_id} "
                        f"пытается обнулить ФАКТ {target_fact.node_id}. "
                        "Это нарушение фундаментального инварианта безопасности."
                    )
