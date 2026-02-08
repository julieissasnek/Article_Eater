"""
Image Pool API Routes
=====================

API routes for managing the local image pool for gallery building.

Date: January 28, 2026
Version: V22.0.0 (Post-Quinean)
"""

from fastapi import APIRouter, HTTPException, Query, Path, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from pathlib import Path as FilePath
import logging

from src.services.image_pool_manager import (
    init_database,
    search_and_download,
    get_all_images,
    get_image_by_id,
    update_image_tags,
    delete_image,
    get_pool_stats,
    get_query_presets,
    export_for_gallery,
    IMAGE_STORAGE_DIR,
    THUMBNAIL_DIR,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/image-pool", tags=["image-pool"])


# =============================================================================
# Request/Response Models
# =============================================================================

class SearchRequest(BaseModel):
    """Request to search and download images."""
    query: str = Field(..., min_length=2, description="Search query")
    source: str = Field("unsplash", description="Image source: unsplash, pexels, pixabay")
    count: int = Field(10, ge=1, le=50, description="Number of images to download")
    feature_tags: List[str] = Field(default_factory=list, description="Initial feature tags")


class UpdateTagsRequest(BaseModel):
    """Request to update image tags."""
    feature_tags: Optional[List[str]] = None
    context_tags: Optional[List[str]] = None
    user_tags: Optional[List[str]] = None
    feature_scores: Optional[Dict[str, float]] = None
    notes: Optional[str] = None


class BatchTagRequest(BaseModel):
    """Request to tag multiple images at once."""
    image_ids: List[str]
    feature_tags: Optional[List[str]] = None
    context_tags: Optional[List[str]] = None
    feature_scores: Optional[Dict[str, float]] = None


class ExportRequest(BaseModel):
    """Request to export images for gallery builder."""
    image_ids: Optional[List[str]] = None
    tagged_only: bool = True


# =============================================================================
# Routes
# =============================================================================

@router.get("/")
async def get_pool_info():
    """Get information about the image pool."""
    init_database()
    stats = get_pool_stats()
    return {
        "status": "ok",
        "stats": stats,
        "presets_available": list(get_query_presets().keys()),
    }


@router.get("/presets")
async def get_presets():
    """Get predefined query presets for environmental psychology concepts."""
    return get_query_presets()


@router.post("/search")
async def search_images(request: SearchRequest, background_tasks: BackgroundTasks):
    """
    Search for images and download them to the local pool.

    Sources:
    - unsplash: Requires UNSPLASH_ACCESS_KEY env var
    - pexels: Requires PEXELS_API_KEY env var
    - pixabay: Requires PIXABAY_API_KEY env var

    Without API keys, demo images from picsum.photos are used.
    """
    init_database()

    try:
        images = search_and_download(
            query=request.query,
            source=request.source,
            count=request.count,
            feature_tags=request.feature_tags
        )

        return {
            "status": "ok",
            "query": request.query,
            "source": request.source,
            "requested": request.count,
            "downloaded": len(images),
            "images": [img.to_dict() for img in images]
        }
    except Exception as e:
        logger.exception("Error searching images")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/images")
async def list_images(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    source: Optional[str] = Query(None),
    query: Optional[str] = Query(None),
    tagged_only: bool = Query(False)
):
    """List images in the pool with optional filters."""
    init_database()

    images = get_all_images(
        limit=limit,
        offset=offset,
        source=source,
        query=query,
        tagged_only=tagged_only
    )

    stats = get_pool_stats()

    return {
        "images": [img.to_dict() for img in images],
        "count": len(images),
        "total": stats["total_images"],
        "offset": offset,
        "limit": limit,
    }


@router.get("/images/{image_id}")
async def get_image_info(image_id: str = Path(...)):
    """Get information about a specific image."""
    image = get_image_by_id(image_id)
    if not image:
        raise HTTPException(status_code=404, detail=f"Image {image_id} not found")
    return image.to_dict()


@router.get("/image/{image_id}")
async def serve_image(image_id: str = Path(...)):
    """Serve the actual image file."""
    image = get_image_by_id(image_id)
    if not image:
        raise HTTPException(status_code=404, detail=f"Image {image_id} not found")

    path = FilePath(image.local_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Image file not found on disk")

    return FileResponse(
        path=str(path),
        media_type="image/jpeg",
        filename=f"{image_id}.jpg"
    )


@router.get("/thumbnail/{image_id}")
async def serve_thumbnail(image_id: str = Path(...)):
    """Serve the thumbnail image."""
    image = get_image_by_id(image_id)
    if not image:
        raise HTTPException(status_code=404, detail=f"Image {image_id} not found")

    path = FilePath(image.thumbnail_path)
    if not path.exists():
        # Fall back to main image
        path = FilePath(image.local_path)

    if not path.exists():
        raise HTTPException(status_code=404, detail="Thumbnail file not found")

    return FileResponse(
        path=str(path),
        media_type="image/jpeg",
        filename=f"thumb_{image_id}.jpg"
    )


@router.put("/images/{image_id}/tags")
async def update_tags(image_id: str, request: UpdateTagsRequest):
    """Update tags and scores for an image."""
    image = get_image_by_id(image_id)
    if not image:
        raise HTTPException(status_code=404, detail=f"Image {image_id} not found")

    success = update_image_tags(
        image_id=image_id,
        feature_tags=request.feature_tags,
        context_tags=request.context_tags,
        user_tags=request.user_tags,
        feature_scores=request.feature_scores,
        notes=request.notes
    )

    if success:
        return {"status": "ok", "image_id": image_id}
    else:
        raise HTTPException(status_code=500, detail="Failed to update tags")


@router.post("/images/batch-tag")
async def batch_tag_images(request: BatchTagRequest):
    """Tag multiple images at once."""
    results = {"success": [], "failed": []}

    for image_id in request.image_ids:
        try:
            success = update_image_tags(
                image_id=image_id,
                feature_tags=request.feature_tags,
                context_tags=request.context_tags,
                feature_scores=request.feature_scores
            )
            if success:
                results["success"].append(image_id)
            else:
                results["failed"].append(image_id)
        except Exception as e:
            results["failed"].append(image_id)

    return results


@router.delete("/images/{image_id}")
async def remove_image(image_id: str = Path(...)):
    """Delete an image from the pool."""
    image = get_image_by_id(image_id)
    if not image:
        raise HTTPException(status_code=404, detail=f"Image {image_id} not found")

    success = delete_image(image_id)
    if success:
        return {"status": "ok", "deleted": image_id}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete image")


@router.get("/stats")
async def get_stats():
    """Get statistics about the image pool."""
    init_database()
    return get_pool_stats()


@router.post("/export")
async def export_images(request: ExportRequest):
    """
    Export images in format suitable for ClaimGalleryBuilder.

    Returns images formatted for use with the gallery builder's image_pool parameter.
    """
    init_database()

    gallery_format = export_for_gallery(
        image_ids=request.image_ids,
        tagged_only=request.tagged_only
    )

    return {
        "count": len(gallery_format),
        "images": gallery_format
    }


@router.post("/preset/{preset_name}")
async def download_preset(
    preset_name: str = Path(...),
    count_per_query: int = Query(5, ge=1, le=20),
    source: str = Query("unsplash")
):
    """
    Download images for all queries in a preset category.

    This is a batch operation that downloads images for each query
    in the specified preset.
    """
    presets = get_query_presets()

    if preset_name not in presets:
        raise HTTPException(
            status_code=404,
            detail=f"Preset '{preset_name}' not found. Available: {list(presets.keys())}"
        )

    preset = presets[preset_name]
    results = {
        "preset": preset_name,
        "label": preset["label"],
        "queries_processed": 0,
        "total_downloaded": 0,
        "by_query": {}
    }

    for query in preset["queries"]:
        try:
            images = search_and_download(
                query=query,
                source=source,
                count=count_per_query,
                feature_tags=preset["feature_tags"]
            )
            results["queries_processed"] += 1
            results["total_downloaded"] += len(images)
            results["by_query"][query] = len(images)
        except Exception as e:
            logger.error(f"Error downloading for query '{query}': {e}")
            results["by_query"][query] = f"error: {str(e)}"

    return results
