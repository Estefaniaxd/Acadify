"""
Tests for pagination utility
"""
import pytest
from src.utils.pagination import (
    PaginationParams, 
    PaginatedResponse, 
    paginate_dict_response,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE
)


class TestPaginationParams:
    """Tests for PaginationParams class"""
    
    def test_default_values(self):
        """Test default pagination parameters"""
        pagination = PaginationParams()
        
        assert pagination.page == 1
        assert pagination.limit == DEFAULT_PAGE_SIZE
        assert pagination.offset == 0
    
    def test_custom_offset(self):
        """Test custom offset"""
        pagination = PaginationParams(offset=100, limit=50)
        
        assert pagination.offset == 100
        assert pagination.page == 3  # (100 / 50) + 1
    
    def test_custom_limit(self):
        """Test custom limit"""
        pagination = PaginationParams(limit=25)
        
        assert pagination.limit == 25
        assert pagination.offset == 0
    
    def test_limit_exceeds_max(self):
        """Test that limit validation works"""
        with pytest.raises(Exception):  # Pydantic ValidationError
            PaginationParams(limit=200)
    
    def test_offset_calculation(self):
        """Test offset calculation for different pages"""
        # Offset 0, limit 10 -> page 1
        p1 = PaginationParams(offset=0, limit=10)
        assert p1.offset == 0
        assert p1.page == 1
        
        # Offset 10, limit 10 -> page 2
        p2 = PaginationParams(offset=10, limit=10)
        assert p2.offset == 10
        assert p2.page == 2
        
        # Offset 100, limit 25 -> page 5
        p5 = PaginationParams(offset=100, limit=25)
        assert p5.offset == 100
        assert p5.page == 5
    
    def test_negative_page(self):
        """Test handling of negative offset"""
        with pytest.raises(Exception):  # Pydantic ValidationError
            PaginationParams(offset=-1)
    
    def test_zero_offset(self):
        """Test handling of zero offset"""
        pagination = PaginationParams(offset=0)
        
        assert pagination.offset == 0
        assert pagination.page == 1


class TestPaginatedResponse:
    """Tests for PaginatedResponse function"""
    
    def test_paginate_dict_response_first_page(self):
        """Test pagination response for first page"""
        data = [{"id": i, "name": f"Item {i}"} for i in range(1, 51)]
        total = 150
        limit = 50
        offset = 0
        
        response = paginate_dict_response(
            data=data,
            total=total,
            limit=limit,
            offset=offset,
            message="Items obtenidos"
        )
        
        assert response["success"] is True
        assert response["message"] == "Items obtenidos"
        assert len(response["data"]) == 50
        assert response["total"] == 150
        assert response["page"] == 1
        assert response["limit"] == 50
        assert response["total_pages"] == 3
        assert response["has_next"] is True
        assert response["has_prev"] is False
    
    def test_paginate_dict_response_middle_page(self):
        """Test pagination response for middle page"""
        data = [{"id": i} for i in range(51, 101)]
        total = 150
        limit = 50
        offset = 50  # page 2
        
        response = paginate_dict_response(
            data=data,
            total=total,
            limit=limit,
            offset=offset
        )
        
        assert response["page"] == 2
        assert response["has_next"] is True
        assert response["has_prev"] is True
    
    def test_paginate_dict_response_last_page(self):
        """Test pagination response for last page"""
        data = [{"id": i} for i in range(101, 151)]
        total = 150
        limit = 50
        offset = 100  # page 3
        
        response = paginate_dict_response(
            data=data,
            total=total,
            limit=limit,
            offset=offset
        )
        
        assert response["page"] == 3
        assert response["has_next"] is False
        assert response["has_prev"] is True
    
    def test_paginate_empty_data(self):
        """Test pagination with empty data"""
        data = []
        total = 0
        limit = 50
        offset = 0
        
        response = paginate_dict_response(
            data=data,
            total=total,
            limit=limit,
            offset=offset
        )
        
        assert response["success"] is True
        assert len(response["data"]) == 0
        assert response["total"] == 0
        assert response["total_pages"] == 0
        assert response["has_next"] is False
        assert response["has_prev"] is False
    
    def test_paginate_single_page(self):
        """Test pagination when all data fits in one page"""
        data = [{"id": i} for i in range(1, 21)]
        total = 20
        limit = 50
        offset = 0
        
        response = paginate_dict_response(
            data=data,
            total=total,
            limit=limit,
            offset=offset
        )
        
        assert response["total_pages"] == 1
        assert response["has_next"] is False
        assert response["has_prev"] is False
    
    def test_paginate_exact_page_boundary(self):
        """Test pagination when total is exact multiple of limit"""
        data = [{"id": i} for i in range(1, 51)]
        total = 100
        limit = 50
        offset = 0
        
        response = paginate_dict_response(
            data=data,
            total=total,
            limit=limit,
            offset=offset
        )
        
        assert response["total_pages"] == 2
        assert response["has_next"] is True
        
        # Test last page
        response2 = paginate_dict_response(
            data=data,
            total=total,
            limit=limit,
            offset=50  # page 2
        )
        
        assert response2["has_next"] is False
