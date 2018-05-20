// #include <QtGui/QPushButton>
// #include <QtGui/QDialog>
// #include <qdatastream.h>

#include <maya/MIOStream.h>
#include <maya/MGlobal.h>
#include <maya/MObject.h>
#include <maya/MTime.h>
#include <maya/MVector.h>
#include <maya/MPlug.h>
#include <maya/MDataBlock.h>
#include <maya/MFnPlugin.h>
// #include <maya/MPxEmitterNode.h>
// #include <maya/MPxNode.h>
//
#include <maya/MPxLocatorNode.h>
// #include <maya/MPxTransform.h>
#include <maya/MPxContext.h>
#include <maya/MPxContextCommand.h>
#include <maya/MPxManipContainer.h>
 
#include <maya/MEvent.h>
// #include <maya/MPxDrawOverride.h>

#include <maya/M3dView.h>
// vp2.0 includes
#include <maya/MDrawRegistry.h>
#include <maya/MPxDrawOverride.h>
#include <maya/MUserData.h>
#include <maya/MDrawContext.h>
#include <maya/MHWGeometryUtilities.h>
// class MIntArray;
// class MDoubleArray;
// class MVectorArray;
// class MFnArrayAttrsData;

// #define McheckErr(stat, msg)		\
//     if ( MS::kSuccess != stat )		\
//     {								\
//         cerr << msg;				\
//         return MS::kFailure;		\
//     }



class sporeLocator : public MPxLocatorNode
{
public:
                            sporeLocator() {};
    virtual				    ~sporeLocator() {};

    virtual MStatus		    compute( const MPlug& plug, MDataBlock& data );
    // virtual bool            isBounded() const;
    // virtual MBoundingBox    boundingBox() const;

    virtual void            draw(
                                M3dView & view, const MDagPath & path,
                                M3dView::DisplayStyle style,
                                M3dView::DisplayStatus status );

    static  void*		    creator();
    static  MStatus		    initialize();

    static	MTypeId		    id;
    static  MString         drawRegistrantId;
    static  MString         drawDbClassification;


    // input attributes
    static  MObject         aInMesh;
    // output attributes
    static  MObject         aInstanceData;
    // context attributes
    static  MObject         aContextMode;
    static  MObject         aBrushRadius;
    static  MObject         aNumBrushSamples;
    static  MObject         aFalloff;
    static  MObject         aAlignSpace;
    static  MObject         aMinDistance;
    static  MObject         aStrength;
    static  MObject         aMinRotation;
    static  MObject         aMaxRotation;
    static  MObject         aUniformScale;
    static  MObject         aMinScale;
    static  MObject         aMaxScale;
    static  MObject         aScaleFactor;
    static  MObject         aScaleAmount;
    static  MObject         aMinOffset;
    static  MObject         aMaxOffset;
    // emit attributes
    static  MObject         aEmitType;
    static  MObject         aEmit;
    static  MObject         aNumEmitSamples;
    static  MObject         aMinRadius;
    static  MObject         aEmitFromTexture;
    static  MObject         aEmitTexture;
    // dummy attributes
    static  MObject         aGeoCached;
    static  MObject         aPointsCached;
    // storage attributes
    static  MObject         aPosition;
    static  MObject         aRotatio;
    static  MObject         aScale;
    static  MObject         aInstanceId;
    static  MObject         aVisibility;
    static  MObject         aNormal;
    static  MObject         aTangent;
    static  MObject         aUCoord;
    static  MObject         aVCoord;
    static  MObject         aPolyId;
    static  MObject         aColor;
    static  MObject         aIndex;
};





/*
class ptcDrawOverride : public MHWRender::MPxDrawOverride
{
public:
	static  MHWRender::MPxDrawOverride* Creator(const MObject& obj)
	{
		return new ptcDrawOverride(obj);
	}

    virtual                 ~ptcDrawOverride();
    virtual                 MHWRender::DrawAPI supportedDrawAPIs() const;

    // virtual bool isBounded(
	//     const MDagPath& objPath,
	//     const MDagPath& cameraPath) const;
    //
	// virtual MBoundingBox boundingBox(
	//     const MDagPath& objPath,
	//     const MDagPath& cameraPath) const;

    virtual MUserData*      prepareForDraw(
                                const MDagPath& objPath,
                                const MDagPath& cameraPath,
                                const MHWRender::MFrameContext& frameContext,
                                MUserData* oldData);

    virtual void            draw(
                                const MHWRender::MDrawContext& context,
                                const MUserData* data );
private:
    ptcDrawOverride(const MObject& obj );
};

class ptcData : public MUserData
{
public:
    ptcData() : MUserData( false ) {}
    virtual ~ptcData() {}

    // MVectorArray position;
};*/


