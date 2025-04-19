from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from ..models.resource import Resource, ResourceStatus, ResourcePriority
import logging
import pandas as pd
from io import BytesIO
from datetime import datetime

logger = logging.getLogger(__name__)

class ResourceService:
    @staticmethod
    def create_resources_from_analysis(
        db: Session,
        script_id: int,
        resource_analysis: Dict[str, Any]
    ) -> List[Resource]:
        """
        从AI分析结果创建资源记录
        """
        try:
            created_resources = []
            
            # 预期resource_analysis的结构：
            # {
            #     "resources_by_type": {
            #         "prop": [...],
            #         "costume": [...],
            #         ...
            #     },
            #     "scene_distribution": {
            #         "resource_name": {
            #             "first_appearance": scene_number,
            #             ...
            #         }
            #     }
            # }
            
            resources_by_type = resource_analysis.get("resources_by_type", {})
            scene_distribution = resource_analysis.get("scene_distribution", {})
            
            for resource_type, resources in resources_by_type.items():
                for resource_name in resources:
                    # 检查资源是否已存在
                    existing_resource = db.query(Resource).filter(
                        Resource.script_id == script_id,
                        Resource.name == resource_name,
                        Resource.type == resource_type
                    ).first()
                    
                    if existing_resource:
                        continue
                    
                    # 获取首次出现的场景编号
                    scene_info = scene_distribution.get(resource_name, {})
                    first_appearance = scene_info.get("first_appearance")
                    
                    # 创建新资源记录
                    new_resource = Resource(
                        script_id=script_id,
                        name=resource_name,
                        type=resource_type,
                        status=ResourceStatus.PENDING,
                        priority=ResourcePriority.MEDIUM,
                        scene_number=first_appearance
                    )
                    
                    db.add(new_resource)
                    created_resources.append(new_resource)
            
            db.commit()
            return created_resources
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating resources from analysis: {str(e)}")
            raise

    @staticmethod
    def update_resource_from_analysis(
        db: Session,
        resource: Resource,
        analysis_data: Dict[str, Any]
    ) -> Resource:
        """
        根据新的分析结果更新资源信息
        """
        try:
            scene_info = analysis_data.get("scene_distribution", {}).get(resource.name, {})
            
            if scene_info:
                # 更新场景相关信息
                if "first_appearance" in scene_info:
                    resource.scene_number = scene_info["first_appearance"]
                
                # 可以添加更多的更新逻辑
                
            db.commit()
            return resource
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating resource from analysis: {str(e)}")
            raise

    @staticmethod
    def export_resources(
        db: Session,
        script_id: Optional[int] = None,
        status: Optional[ResourceStatus] = None,
        resource_type: Optional[str] = None,
        format: str = "xlsx"
    ) -> BytesIO:
        """
        导出资源列表为Excel文件
        """
        try:
            # 构建查询
            query = db.query(Resource)
            if script_id:
                query = query.filter(Resource.script_id == script_id)
            if status:
                query = query.filter(Resource.status == status)
            if resource_type:
                query = query.filter(Resource.type == resource_type)

            resources = query.all()

            # 准备数据
            data = []
            for resource in resources:
                data.append({
                    "资源ID": resource.id,
                    "名称": resource.name,
                    "类型": resource.type,
                    "状态": resource.status.value,
                    "优先级": resource.priority.value,
                    "描述": resource.description,
                    "预估预算": resource.estimated_budget,
                    "实际预算": resource.actual_budget,
                    "负责人": resource.responsible_person,
                    "备注": resource.notes,
                    "需要日期": resource.needed_by.strftime("%Y-%m-%d") if resource.needed_by else None,
                    "首次出现场景": resource.scene_number,
                    "创建时间": resource.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "更新时间": resource.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                })

            # 创建DataFrame
            df = pd.DataFrame(data)

            # 创建输出缓冲区
            output = BytesIO()
            
            if format == "xlsx":
                # 创建Excel writer
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, sheet_name='资源列表', index=False)
                    
                    # 获取workbook和worksheet对象
                    workbook = writer.book
                    worksheet = writer.sheets['资源列表']
                    
                    # 设置列宽
                    for i, col in enumerate(df.columns):
                        max_length = max(
                            df[col].astype(str).apply(len).max(),
                            len(col)
                        )
                        worksheet.set_column(i, i, max_length + 2)
                    
                    # 添加格式
                    header_format = workbook.add_format({
                        'bold': True,
                        'bg_color': '#D9D9D9',
                        'border': 1
                    })
                    
                    # 应用格式到表头
                    for col_num, value in enumerate(df.columns.values):
                        worksheet.write(0, col_num, value, header_format)

            elif format == "csv":
                df.to_csv(output, index=False, encoding='utf-8-sig')
            
            # 将指针移到开始
            output.seek(0)
            return output

        except Exception as e:
            logger.error(f"Error exporting resources: {str(e)}")
            raise

    @staticmethod
    def get_resource_statistics(
        db: Session,
        script_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        获取资源统计信息
        """
        try:
            # 基础查询
            base_query = db.query(Resource)
            if script_id:
                base_query = base_query.filter(Resource.script_id == script_id)

            # 1. 按类型统计
            type_stats = (
                base_query
                .with_entities(Resource.type, func.count(Resource.id))
                .group_by(Resource.type)
                .all()
            )
            type_summary = {t: c for t, c in type_stats}

            # 2. 按状态统计
            status_stats = (
                base_query
                .with_entities(Resource.status, func.count(Resource.id))
                .group_by(Resource.status)
                .all()
            )
            status_summary = {s.value: c for s, c in status_stats}

            # 3. 按优先级统计
            priority_stats = (
                base_query
                .with_entities(Resource.priority, func.count(Resource.id))
                .group_by(Resource.priority)
                .all()
            )
            priority_summary = {p.value: c for p, c in priority_stats}

            # 4. 预算统计
            budget_stats = db.query(
                func.count(Resource.id).label('total_count'),
                func.sum(Resource.estimated_budget).label('total_estimated_budget'),
                func.sum(Resource.actual_budget).label('total_actual_budget'),
                func.avg(Resource.estimated_budget).label('avg_estimated_budget'),
                func.avg(Resource.actual_budget).label('avg_actual_budget')
            ).filter(base_query.whereclause).first()

            # 5. 时间分布统计
            time_stats = (
                base_query
                .with_entities(
                    func.date_trunc('month', Resource.needed_by).label('month'),
                    func.count(Resource.id)
                )
                .filter(Resource.needed_by.isnot(None))
                .group_by('month')
                .order_by('month')
                .all()
            )
            time_distribution = {
                month.strftime("%Y-%m") if month else "未设置": count 
                for month, count in time_stats
            }

            # 6. 计算完成率
            total_resources = base_query.count()
            completed_resources = base_query.filter(
                Resource.status == ResourceStatus.COMPLETED
            ).count()
            completion_rate = (completed_resources / total_resources * 100) if total_resources > 0 else 0

            # 7. 预算执行情况
            budget_execution = {
                "total_estimated": budget_stats.total_estimated_budget or 0,
                "total_actual": budget_stats.total_actual_budget or 0,
                "budget_usage_rate": (
                    (budget_stats.total_actual_budget / budget_stats.total_estimated_budget * 100)
                    if budget_stats.total_estimated_budget
                    else 0
                )
            }

            return {
                "summary": {
                    "total_resources": total_resources,
                    "completion_rate": round(completion_rate, 2),
                    "total_estimated_budget": budget_stats.total_estimated_budget,
                    "total_actual_budget": budget_stats.total_actual_budget,
                },
                "type_distribution": type_summary,
                "status_distribution": status_summary,
                "priority_distribution": priority_summary,
                "budget_statistics": {
                    "total_count": budget_stats.total_count,
                    "total_estimated_budget": budget_stats.total_estimated_budget,
                    "total_actual_budget": budget_stats.total_actual_budget,
                    "average_estimated_budget": round(budget_stats.avg_estimated_budget or 0, 2),
                    "average_actual_budget": round(budget_stats.avg_actual_budget or 0, 2)
                },
                "time_distribution": time_distribution,
                "budget_execution": budget_execution
            }

        except Exception as e:
            logger.error(f"Error generating resource statistics: {str(e)}")
            raise

    @staticmethod
    def export_statistics(
        db: Session,
        script_id: Optional[int] = None,
        format: str = "xlsx"
    ) -> BytesIO:
        """
        导出资源统计报告
        """
        try:
            # 获取统计数据
            stats = ResourceService.get_resource_statistics(db, script_id)
            
            # 创建多个DataFrame用于不同的统计表
            summary_df = pd.DataFrame([stats['summary']])
            
            type_df = pd.DataFrame(
                stats['type_distribution'].items(),
                columns=['资源类型', '数量']
            )
            
            status_df = pd.DataFrame(
                stats['status_distribution'].items(),
                columns=['状态', '数量']
            )
            
            priority_df = pd.DataFrame(
                stats['priority_distribution'].items(),
                columns=['优先级', '数量']
            )
            
            budget_df = pd.DataFrame([stats['budget_statistics']])
            
            time_df = pd.DataFrame(
                stats['time_distribution'].items(),
                columns=['月份', '数量']
            )

            # 创建输出缓冲区
            output = BytesIO()
            
            if format == "xlsx":
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    # 写入各个表
                    summary_df.to_excel(writer, sheet_name='总体概况', index=False)
                    type_df.to_excel(writer, sheet_name='类型分布', index=False)
                    status_df.to_excel(writer, sheet_name='状态分布', index=False)
                    priority_df.to_excel(writer, sheet_name='优先级分布', index=False)
                    budget_df.to_excel(writer, sheet_name='预算统计', index=False)
                    time_df.to_excel(writer, sheet_name='时间分布', index=False)
                    
                    # 获取workbook对象
                    workbook = writer.book
                    
                    # 为每个sheet添加格式
                    for sheet_name in writer.sheets:
                        worksheet = writer.sheets[sheet_name]
                        
                        # 设置列宽
                        for i in range(worksheet.dim_colmax + 1):
                            worksheet.set_column(i, i, 15)
                        
                        # 添加表头格式
                        header_format = workbook.add_format({
                            'bold': True,
                            'bg_color': '#D9D9D9',
                            'border': 1
                        })
                        
                        # 应用表头格式
                        for col_num in range(worksheet.dim_colmax + 1):
                            worksheet.write(0, col_num, worksheet.table[0][col_num], header_format)

            elif format == "csv":
                # CSV格式只导出总体概况
                summary_df.to_csv(output, index=False, encoding='utf-8-sig')
            
            output.seek(0)
            return output

        except Exception as e:
            logger.error(f"Error exporting statistics: {str(e)}")
            raise

    @staticmethod
    def get_cost_analysis(
        db: Session,
        script_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        获取详细的成本分析
        """
        try:
            # 基础查询
            base_query = db.query(Resource)
            if script_id:
                base_query = base_query.filter(Resource.script_id == script_id)

            # 1. 按资源类型的成本分析
            cost_by_type = (
                base_query
                .with_entities(
                    Resource.type,
                    func.sum(Resource.estimated_budget).label('total_estimated'),
                    func.sum(Resource.actual_budget).label('total_actual'),
                    func.count(Resource.id).label('count')
                )
                .group_by(Resource.type)
                .all()
            )

            type_costs = {}
            for t in cost_by_type:
                type_costs[t.type] = {
                    "total_estimated": float(t.total_estimated or 0),
                    "total_actual": float(t.total_actual or 0),
                    "count": t.count,
                    "average_cost": float(t.total_actual or 0) / t.count if t.count > 0 else 0,
                    "variance": float((t.total_actual or 0) - (t.total_estimated or 0)),
                    "variance_percentage": (
                        ((float(t.total_actual or 0) - float(t.total_estimated or 0)) / float(t.total_estimated or 1)) * 100
                        if t.total_estimated
                        else 0
                    )
                }

            # 2. 超支分析
            overbudget_resources = (
                base_query
                .filter(Resource.actual_budget > Resource.estimated_budget)
                .order_by((Resource.actual_budget - Resource.estimated_budget).desc())
                .limit(10)
                .all()
            )

            overbudget_details = [{
                "id": r.id,
                "name": r.name,
                "type": r.type,
                "estimated": float(r.estimated_budget or 0),
                "actual": float(r.actual_budget or 0),
                "variance": float((r.actual_budget or 0) - (r.estimated_budget or 0)),
                "variance_percentage": (
                    ((float(r.actual_budget or 0) - float(r.estimated_budget or 0)) / float(r.estimated_budget or 1)) * 100
                    if r.estimated_budget
                    else 0
                )
            } for r in overbudget_resources]

            # 3. 月度成本趋势
            monthly_costs = (
                base_query
                .with_entities(
                    func.date_trunc('month', Resource.needed_by).label('month'),
                    func.sum(Resource.estimated_budget).label('estimated'),
                    func.sum(Resource.actual_budget).label('actual')
                )
                .filter(Resource.needed_by.isnot(None))
                .group_by('month')
                .order_by('month')
                .all()
            )

            cost_trends = {
                month.strftime("%Y-%m") if month else "未设置": {
                    "estimated": float(estimated or 0),
                    "actual": float(actual or 0),
                    "variance": float((actual or 0) - (estimated or 0))
                }
                for month, estimated, actual in monthly_costs
            }

            # 4. 成本效率分析
            total_stats = db.query(
                func.sum(Resource.estimated_budget).label('total_estimated'),
                func.sum(Resource.actual_budget).label('total_actual'),
                func.count(Resource.id).label('total_count')
            ).filter(base_query.whereclause).first()

            efficiency_metrics = {
                "average_cost_per_resource": (
                    float(total_stats.total_actual or 0) / total_stats.total_count
                    if total_stats.total_count > 0
                    else 0
                ),
                "budget_accuracy": (
                    (1 - abs(float(total_stats.total_actual or 0) - float(total_stats.total_estimated or 0)) 
                     / float(total_stats.total_estimated or 1)) * 100
                    if total_stats.total_estimated
                    else 0
                ),
                "total_variance": float((total_stats.total_actual or 0) - (total_stats.total_estimated or 0)),
                "total_variance_percentage": (
                    ((float(total_stats.total_actual or 0) - float(total_stats.total_estimated or 0)) 
                     / float(total_stats.total_estimated or 1)) * 100
                    if total_stats.total_estimated
                    else 0
                )
            }

            # 5. 状态相关的成本分析
            status_costs = (
                base_query
                .with_entities(
                    Resource.status,
                    func.sum(Resource.estimated_budget).label('estimated'),
                    func.sum(Resource.actual_budget).label('actual'),
                    func.count(Resource.id).label('count')
                )
                .group_by(Resource.status)
                .all()
            )

            costs_by_status = {
                status.value: {
                    "estimated": float(estimated or 0),
                    "actual": float(actual or 0),
                    "count": count,
                    "average": float(actual or 0) / count if count > 0 else 0
                }
                for status, estimated, actual, count in status_costs
            }

            return {
                "summary": {
                    "total_estimated_budget": float(total_stats.total_estimated or 0),
                    "total_actual_budget": float(total_stats.total_actual or 0),
                    "total_variance": efficiency_metrics["total_variance"],
                    "budget_accuracy": round(efficiency_metrics["budget_accuracy"], 2)
                },
                "costs_by_type": type_costs,
                "costs_by_status": costs_by_status,
                "overbudget_analysis": {
                    "top_overbudget_resources": overbudget_details,
                    "total_overbudget_count": len(overbudget_details)
                },
                "monthly_trends": cost_trends,
                "efficiency_metrics": efficiency_metrics
            }

        except Exception as e:
            logger.error(f"Error generating cost analysis: {str(e)}")
            raise

    @staticmethod
    def export_cost_analysis(
        db: Session,
        script_id: Optional[int] = None,
        format: str = "xlsx"
    ) -> BytesIO:
        """
        导出成本分析报告
        """
        try:
            # 获取成本分析数据
            cost_analysis = ResourceService.get_cost_analysis(db, script_id)
            
            # 创建多个DataFrame用于不同的分析表
            summary_df = pd.DataFrame([cost_analysis['summary']])
            
            # 类型成本分析
            type_costs_data = []
            for type_name, costs in cost_analysis['costs_by_type'].items():
                costs['type'] = type_name
                type_costs_data.append(costs)
            type_costs_df = pd.DataFrame(type_costs_data)
            
            # 状态成本分析
            status_costs_data = []
            for status, costs in cost_analysis['costs_by_status'].items():
                costs['status'] = status
                status_costs_data.append(costs)
            status_costs_df = pd.DataFrame(status_costs_data)
            
            # 超支资源分析
            overbudget_df = pd.DataFrame(cost_analysis['overbudget_analysis']['top_overbudget_resources'])
            
            # 月度趋势分析
            trends_data = []
            for month, data in cost_analysis['monthly_trends'].items():
                data['month'] = month
                trends_data.append(data)
            trends_df = pd.DataFrame(trends_data)
            
            # 创建输出缓冲区
            output = BytesIO()
            
            if format == "xlsx":
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    # 写入各个表
                    summary_df.to_excel(writer, sheet_name='总体概况', index=False)
                    type_costs_df.to_excel(writer, sheet_name='类型成本分析', index=False)
                    status_costs_df.to_excel(writer, sheet_name='状态成本分析', index=False)
                    overbudget_df.to_excel(writer, sheet_name='超支分析', index=False)
                    trends_df.to_excel(writer, sheet_name='月度趋势', index=False)
                    
                    # 获取workbook对象
                    workbook = writer.book
                    
                    # 为每个sheet添加格式
                    for sheet_name in writer.sheets:
                        worksheet = writer.sheets[sheet_name]
                        
                        # 设置列宽
                        for i in range(worksheet.dim_colmax + 1):
                            worksheet.set_column(i, i, 15)
                        
                        # 添加表头格式
                        header_format = workbook.add_format({
                            'bold': True,
                            'bg_color': '#D9D9D9',
                            'border': 1
                        })
                        
                        # 添加数字格式
                        number_format = workbook.add_format({'num_format': '#,##0.00'})
                        percent_format = workbook.add_format({'num_format': '0.00%'})
                        
                        # 应用格式
                        for col_num in range(worksheet.dim_colmax + 1):
                            worksheet.write(0, col_num, worksheet.table[0][col_num], header_format)
                            
                            # 对数字列应用格式
                            if any(key in worksheet.table[0][col_num].lower() 
                                  for key in ['budget', 'cost', 'variance', 'estimated', 'actual']):
                                worksheet.set_column(col_num, col_num, 15, number_format)
                            elif 'percentage' in worksheet.table[0][col_num].lower():
                                worksheet.set_column(col_num, col_num, 15, percent_format)

            elif format == "csv":
                # CSV格式只导出总体概况和超支分析
                summary_df.to_csv(output, index=False, encoding='utf-8-sig')
            
            output.seek(0)
            return output

        except Exception as e:
            logger.error(f"Error exporting cost analysis: {str(e)}")
            raise 