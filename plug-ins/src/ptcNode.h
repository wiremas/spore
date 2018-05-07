#include <QtGui/QPushButton>
#include <QtGui/QDialog>
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



class ptcNode : public MPxLocatorNode
{
public:
                            ptcNode() {};
    virtual				    ~ptcNode() {};

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
    static  MObject         inMesh;
    static  MObject         aEmitRequest;
    static  MObject         aInputPoints;

    // node attributes
    static  MObject         aNumSamples;
    static  MObject         aNumInstances;
    static  MObject         aPointVisibility;
    static  MObject         aDisplaySize;
    static  MObject         aBrushRadius;

    // output attributes
    static  MObject         instanceData;
};


//
// Brush Context
//


class brushContext : public MPxContext
{
public:
                            brushContext();
    virtual void            toolOnSetup( MEvent& event );

    virtual MStatus         doPress( MEvent &event );
    virtual MStatus         doDrag( MEvent &event );
    virtual MStatus         doEnterRegion( MEvent &event );
    // MStatus                 doPress( MEvent &event ) override;
    // MStatus                 doPress (MEvent & event, MHWRender::MUIDrawManager& drawMgr, const MHWRender::MFrameContext& context) override;

    static void             updateManipulators( void *data );

    static MPoint           screenToWorld( MEvent &event );

    static MObject          targetSurface;
private:
    static M3dView                 view;
};


//
// Context Command
//


class brushContextCmd : public MPxContextCommand
{
public:
                            brushContextCmd() {};
    static void*            creator();
    virtual MPxContext*     makeObj();

};


//
// Brush Manipulator Container
//


class brushManip : public MPxManipContainer
{
public:
                            brushManip() {};
    virtual                 ~brushManip() {};

    static void *           creator();
    static MStatus          initialize();

    virtual void            draw( M3dView &view,
                                const MDagPath &path,
                                M3dView::DisplayStyle style,
                                M3dView::DisplayStatus status );
    virtual MStatus         connectToDependNode( const MObject &node );

    // virtual MStatus         doPress();
    // virtual MStatus         doDrag();

    static MTypeId          id;
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


